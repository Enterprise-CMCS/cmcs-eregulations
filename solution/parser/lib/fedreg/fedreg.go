package fedreg

import (
	"context"
	"encoding/json"
	"encoding/xml"
	"fmt"
	"io"
	"net/url"
	"regexp"
	"strings"

	"github.com/cmsgov/cmcs-eregulations/lib/network"

	log "github.com/sirupsen/logrus"
)

// FedRegContentURL is the Federal Register API endpoint to retrieve a list of documents from
var FedRegContentURL = "https://www.federalregister.gov/api/v1/documents.json?fields[]=type&fields[]=full_text_xml_url&fields[]=citation&fields[]=docket_ids&fields[]=document_number&fields[]=html_url&fields[]=publication_date&fields[]=title&fields[]=raw_text_url&order=newest&conditions[cfr][title]=%d&conditions[cfr][part]=%s"

// FRDoc is the Federal Register's representation of a document
type FRDoc struct {
	Name           string   `json:"citation"`
	Description    string   `json:"title"`
	Category       string   `json:"type"`
	URL            string   `json:"html_url"`
	Date           string   `json:"publication_date"`
	DocketNumbers  []string `json:"docket_ids"`
	DocumentNumber string   `json:"document_number"`
	FullTextURL    string   `json:"full_text_xml_url"`
	RawTextURL	   string	`json:"raw_text_url"`
}

// FRDocPage represents a page containing many documents. NextPageURL is optional and points to the next page of docs, if one exists
type FRDocPage struct {
	NextPageURL string   `json:"next_page_url"`
	Results     []*FRDoc `json:"results"`
}

func fetch(ctx context.Context, path string) (io.Reader, error) {
	frURL, err := url.Parse(path)
	if err != nil {
		return nil, fmt.Errorf("failed to parse URL: %+v", err)
	}

	reader, code, err := network.Fetch(ctx, frURL, false)
	if err != nil {
		if code != -1 {
			return nil, fmt.Errorf("fetch failed with code %d: %+v", code, err)
		}
		return nil, fmt.Errorf("fetch failed: %+v", err)
	}

	return reader, nil
}

// FetchContent retrieves a list of FR docs from the Federal Register
func FetchContent(ctx context.Context, title int, part string) ([]*FRDoc, error) {
	startPath := fmt.Sprintf(FedRegContentURL, title, part)
	return fetchContent(ctx, startPath)
}

func fetchContent(ctx context.Context, path string) ([]*FRDoc, error) {
	reader, err := fetch(ctx, path)
	if err != nil {
		return nil, err
	}

	var p FRDocPage
	d := json.NewDecoder(reader)
	if err := d.Decode(&p); err != nil {
		return nil, fmt.Errorf("decode failed: %+v", err)
	}

	c := p.Results
	if p.NextPageURL != "" {
		docs, err := fetchContent(ctx, p.NextPageURL)
		if err != nil {
			return nil, err
		}
		c = append(c, docs...)
	}

	return c, nil
}

// XMLQuery represents the inner value of an XML tag
type XMLQuery struct {
	Loc string `xml:",chardata"`
}

// FetchSections pulls the full document from the Federal Register and extracts all SECTNO tags
// Returns a list of sections and a map of parts => titles
func FetchSections(ctx context.Context, path string, titles map[string]struct{}) ([]string, []string, map[string]string, error) {
	reader, err := fetch(ctx, path)
	if err != nil {
		return nil, nil, nil, err
	}

	cfrs := make(map[string]string)
	var sections []string
	var ranges []string

	d := xml.NewDecoder(reader)
	for {
		t, err := d.Token()
		if err != nil {
			if err == io.EOF {
				break
			}
			return nil, nil, nil, fmt.Errorf("failed to decode XML: %+v", err)
		}
		if se, ok := t.(xml.StartElement); ok {
			if se.Name.Local == "SECTNO" || se.Name.Local == "CFR" {
				var l XMLQuery
				err = d.DecodeElement(&l, &se)
				if err != nil {
					return nil, nil, nil, fmt.Errorf("failed to decode element: %+v", err)
				}
				if se.Name.Local == "CFR" {
					// extract CFR information and put it in the CFR table
					title, parts, err := extractCFR(l.Loc)
					if err != nil {
						log.Warn("[fedreg] failed to extract CFR information from '", l.Loc, "': ", err)
					} else if _, exists := titles[title]; exists {
						for _, part := range parts {
							if _, exists := cfrs[part]; !exists {
								cfrs[part] = title
							}
						}
					}
				} else if se.Name.Local == "SECTNO" {
					section, sectionRanges, err := extractSection(l.Loc)
					if err != nil {
						log.Warn("[fedreg] ", err)
					} else if sectionRanges != "" {
						ranges = append(ranges, sectionRanges)
					} else {
						sections = append(sections, section)
					}
				}
			}
		}
	}

	return sections, ranges, cfrs, nil
}

func extractSection(input string) (string, string, error) {
	rangePat := regexp.MustCompile(`\d+\.\d+-\d+\.\d+`)
	pat := regexp.MustCompile(`\d+\.\d+`)
	r := rangePat.FindString(input)
	if r != "" {
		return "", r, nil
	}
	s := pat.FindString(input)
	if s == "" {
		return s, "", fmt.Errorf("failed to extract section from %s", input)
	}
	return s, "", nil
}

func extractCFR(input string) (string, []string, error) {
	var parts []string
	split := strings.Split(input, " ")
	if len(split) < 1 {
		return "", nil, fmt.Errorf("the CFR string is empty")
	}

	//extract title
	title := split[0]
	if !regexp.MustCompile(`\d+`).MatchString(title) {
		return "", nil, fmt.Errorf("title '%s' is not a valid title", title)
	}

	for _, p := range split[1:] {
		part := strings.Trim(strings.TrimSpace(p), ".,;:")
		if regexp.MustCompile(`\d+`).MatchString(part) {
			parts = append(parts, part)
		}
	}

	if len(parts) < 1 {
		return "", nil, fmt.Errorf("parts list is empty")
	}

	return title, parts, nil
}
