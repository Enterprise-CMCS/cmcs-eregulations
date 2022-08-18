package eregs

import (
	"context"
	"encoding/json"
	"fmt"
	"net/url"
	"os"
	"path"
	"strings"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/network"

	log "github.com/sirupsen/logrus"
)

// BaseURL is the URL of the eRegs API
var BaseURL string

// DocumentURL is the relative path to post FR documents to
var DocumentURL = "/resources/federal_register_docs"

// DocListURL is the relative path to retrieve a list of FR docs that eRegs already has
var DocListURL = "/resources/federal_register_docs/doc_numbers"

var postAuth = &network.PostAuth{
	Username: os.Getenv("EREGS_USERNAME"),
	Password: os.Getenv("EREGS_PASSWORD"),
}

// Section represents a section identifier in the eRegs supplemental content system
type Section struct {
	Title   string `json:"title"`
	Part    string `json:"part"`
	Section string `json:"section_id"`
}

// FRDoc is eRegs' representation of Federal Register documents, including a list of sections
type FRDoc struct {
	Name           string     `json:"name"`
	Description    string     `json:"description"`
	DocType        string     `json:"doc_type"`
	URL            string     `json:"url"`
	Date           string     `json:"date"`
	DocketNumbers  []string   `json:"docket_numbers"`
	DocumentNumber string     `json:"document_number"`
	Locations      []*Section `json:"locations"`
}

// SendDocument attempts to PUT the given FRDoc to eRegs BaseURL+DocumentURL
func SendDocument(ctx context.Context, doc *FRDoc) error {
	eregsURL, err := url.Parse(BaseURL)
	if err != nil {
		return fmt.Errorf("failed to parse eRegs URL \"%s\": %+v", BaseURL, err)
	}
	eregsURL.Path = path.Join(eregsURL.Path, DocumentURL)
	code, err := network.SendJSON(ctx, eregsURL, doc, true, postAuth, network.HTTPPut)
	if err != nil {
		if code != -1 {
			return fmt.Errorf("send failed with code %d: %+v", code, err)
		}
		return fmt.Errorf("send failed: %+v", err)
	}
	return nil
}

// CreateSections takes a list of strings and converts it to proper section identifiers
func CreateSections(title string, s []string) []*Section {
	var sections []*Section

	for _, section := range s {
		sp := strings.Split(section, ".")
		if len(sp) != 2 || sp[0] == "" || sp[1] == "" {
			log.Warn("[eregs] Section identifier ", section, " is invalid.")
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

// FetchDocumentList retrieves a list of URLs for each FR document already stored in Regs
func FetchDocumentList(ctx context.Context) ([]string, error) {
	eregsURL, err := url.Parse(BaseURL)
	if err != nil {
		return nil, fmt.Errorf("failed to parse eRegs URL \"%s\": %+v", BaseURL, err)
	}
	eregsURL.Path = path.Join(eregsURL.Path, DocListURL)

	reader, code, err := network.Fetch(ctx, eregsURL, true)
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
