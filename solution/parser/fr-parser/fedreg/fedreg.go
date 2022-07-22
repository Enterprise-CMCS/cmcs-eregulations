package fedreg

import (
	"context"
	"encoding/json"
	"encoding/xml"
	"fmt"
	"io"
	"net/url"
	"regexp"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/network"

	log "github.com/sirupsen/logrus"
)

// FedRegContentURL is the Federal Register API endpoint to retrieve a list of documents from
var FedRegContentURL = "https://www.federalregister.gov/api/v1/documents.json?fields[]=type&fields[]=full_text_xml_url&fields[]=citation&fields[]=docket_id&fields[]=document_number&fields[]=html_url&fields[]=publication_date&fields[]=title&order=newest&conditions[cfr][title]=%d&conditions[cfr][part]=%s"

// FRDoc is the Federal Register's representation of a document
type FRDoc struct {
	Name           string `json:"citation"`
	Description    string `json:"title"`
	Category       string `json:"type"`
	URL            string `json:"html_url"`
	Date           string `json:"publication_date"`
	DocketNumber   string `json:"docket_id"`
	DocumentNumber string `json:"document_number"`
	FullTextURL    string `json:"full_text_xml_url"`
}

// FRDocPage represents a page containing many documents. NextPageURL is optional and points to the next page of docs, if one exists
type FRDocPage struct {
	NextPageURL string   `json:"next_page_url"`
	Results     []*FRDoc `json:"results"`
}

func fetch(ctx context.Context, path string) (io.Reader, error) {
	frURL, err := url.Parse(path)
	if err != nil {
		return nil, fmt.Errorf("Failed to parse URL: %+v", err)
	}

	reader, code, err := network.Fetch(ctx, frURL, false)
	if err != nil {
		if code != -1 {
			return nil, fmt.Errorf("Fetch failed with code %d: %+v", code, err)
		}
		return nil, fmt.Errorf("Fetch failed: %+v", err)
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
		return nil, fmt.Errorf("Decode failed: %+v", err)
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
func FetchSections(ctx context.Context, path string) ([]string, error) {
	reader, err := fetch(ctx, path)
	if err != nil {
		return nil, err
	}

	var sections []string
	d := xml.NewDecoder(reader)
	for {
		t, err := d.Token()
		if err != nil {
			if err == io.EOF {
				break
			}
			return nil, fmt.Errorf("Failed to decode XML: %+v", err)
		}
		if se, ok := t.(xml.StartElement); ok {
			if se.Name.Local == "SECTNO" {
				var l XMLQuery
				err = d.DecodeElement(&l, &se)
				if err != nil {
					return nil, fmt.Errorf("Failed to decode element: %+v", err)
				}
				section, err := extractSection(l.Loc)
				if err != nil {
					log.Error("[fedreg] Failed to extract section from identifier \"", l.Loc, "\"")
				} else {
					sections = append(sections, section)
				}
			}
		}
	}

	return sections, nil
}

func extractSection(input string) (string, error) {
	pat := regexp.MustCompile(`\d+\.\d+`)
	s := pat.FindString(input)
	if s == "" {
		return s, fmt.Errorf("Failed to extract section from %s", input)
	}
	return s, nil
}
