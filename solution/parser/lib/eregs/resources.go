package eregs

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"

	"github.com/cmsgov/cmcs-eregulations/lib/network"

	log "github.com/sirupsen/logrus"
)

// DocumentURL is the relative path to post FR documents to
var DocumentURL = "/resources/public/federal_register_links"

// DocListURL is the relative path to retrieve a list of FR docs that eRegs already has
var DocListURL = "/resources/public/federal_register_links/document_numbers"

// Section represents a section identifier in the eRegs supplemental content system
type Section struct {
	Title   string `json:"title"`
	Part    string `json:"part"`
	Section string `json:"section_id"`
}

// SectionRanges represents a range of sections in the eregs supplemental content
type SectionRanges struct {
	Title    string `json:"title"`
	Part     string `json:"part"`
	FirstSec string `json:"first_sec"`
	LastSec  string `json:"last_sec"`
}

// FRDoc is eRegs' representation of Federal Register documents, including a list of sections
type FRDoc struct {
	Name           string           `json:"name"`
	Description    string           `json:"description"`
	DocType        string           `json:"doc_type"`
	URL            string           `json:"url"`
	Date           string           `json:"date"`
	DocketNumbers  []string         `json:"docket_numbers"`
	DocumentNumber string           `json:"document_number"`
	Sections       []*Section       `json:"sections"`
	SectionRanges  []*SectionRanges `json:"section_ranges"`
	RawTextURL     string           `json:"raw_text_url"`
}

// SendDocument attempts to PUT the given FRDoc to eRegs BaseURL+DocumentURL
func SendDocument(ctx context.Context, doc *FRDoc) error {
	u, err := parseURL(DocumentURL)
	if err != nil {
		return fmt.Errorf("failed to parse eRegs URL '%s': %+v", BaseURL, err)
	}

	code, err := network.SendJSON(ctx, u, doc, true, PostAuth, network.HTTPPut)
	if err != nil {
		if code != -1 {
			return fmt.Errorf("send failed with code %d: %+v", code, err)
		}
		return fmt.Errorf("send failed: %+v", err)
	}
	return nil
}

// CreateSections takes a list of strings and converts it to proper section identifiers
func CreateSections(s []string, pm map[string]string) []*Section {
	var sections []*Section

	for _, section := range s {
		sp := strings.Split(section, ".")
		if len(sp) != 2 || sp[0] == "" || sp[1] == "" {
			log.Warn("[eregs] Section identifier ", section, " is invalid.")
			continue
		}

		title, exists := pm[sp[0]]
		if !exists {
			log.Warn("[eregs] Section identifier ", section, " has no matching title.")
			continue
		}

		s := &Section{
			Title:   title,
			Part:    sp[0],
			Section: sp[1],
		}

		sections = append(sections, s)
	}

	return sections
}

// CreateSectionRanges get a list of ranges and converts them into the range objects
func CreateSectionRanges(s []string, pm map[string]string) []*SectionRanges {
	var ranges []*SectionRanges

	for _, secRange := range s {

		splitSections := strings.Split(secRange, "-")
		if len(splitSections) != 2 || splitSections[0] == "" || splitSections[1] == "" {
			log.Warn("[eregs] section range ", secRange, "is invalid")
			continue
		}
		sections := CreateSections(splitSections, pm)

		if len(sections) != 2 {
			log.Warn("[eregs] section range ", secRange, "is invalid")
			continue
		}

		title := pm[sections[0].Part]

		if sections[0].Part != sections[1].Part {
			log.Warn("[eregs] Section identifier ", secRange, "  contains different parts.")
			continue
		}

		s := &SectionRanges{
			Title:    title,
			Part:     sections[0].Part,
			FirstSec: sections[0].Section,
			LastSec:  sections[1].Section,
		}

		ranges = append(ranges, s)
	}
	return ranges
}

// FetchDocumentList retrieves a list of URLs for each FR document already stored in Regs
func FetchDocumentList(ctx context.Context) ([]string, error) {
	u, err := parseURL(DocListURL)
	if err != nil {
		return nil, fmt.Errorf("failed to parse eRegs URL '%s': %+v", BaseURL, err)
	}

	reader, code, err := network.Fetch(ctx, u, true, getAuth())
	if err != nil {
		if code != -1 {
			return nil, fmt.Errorf("fetch failed with code %d: %+v", code, err)
		}
		return nil, fmt.Errorf("fetch failed: %+v", err)
	}

	var docs []string
	d := json.NewDecoder(reader)
	err = d.Decode(&docs)
	if err != nil {
		return nil, fmt.Errorf("failed to parse JSON response: %+v", err)
	}

	return docs, nil
}
