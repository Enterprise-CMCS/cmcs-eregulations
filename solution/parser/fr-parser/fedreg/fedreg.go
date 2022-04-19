package fedreg

import (
	"context"
	"net/url"
	"fmt"
	"encoding/json"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/network"
)

var FedRegURL= "https://www.federalregister.gov/api/v1/documents.json?fields[]=type&fields[]=abstract&fields[]=citation&fields[]=correction_of&fields[]=action&fields[]=dates&fields[]=docket_id&fields[]=docket_ids&fields[]=document_number&fields[]=effective_on&fields[]=html_url&fields[]=publication_date&fields[]=regulation_id_number_info&fields[]=regulation_id_numbers&fields[]=title&order=newest&conditions[cfr][title]=%d&conditions[cfr][part]=%s"

type FRDoc struct {
	Name string `json:"citation"`
	Description string `json:"title"`
	Category string `json:"type"`
	URL string `json:"html_url"`
	Date string `json:"publication_date"`
	DocketNumber string `json:"docket_id"`
	DocumentNumber string `json:"document_number"`
}

type FRDocPage struct {
	NextPageURL string `json:"next_page_url"`
	Results []*FRDoc `json:"results"`
}

func FetchContent(ctx context.Context, title int, part string) ([]*FRDoc, error) {
	startPath := fmt.Sprintf(FedRegURL, title, part)
	return fetchContent(ctx, startPath)
}

func fetchContent(ctx context.Context, path string) ([]*FRDoc, error) {
	frURL, err := url.Parse(path)
	if err != nil {
		return nil, err
	}

	reader, code, err := network.Fetch(ctx, frURL, false)
	if err != nil {
		if code != -1 {
			return nil, fmt.Errorf("Fetch failed with code %d: %+v", err)
		}
		return nil, fmt.Errorf("Fetch failed: %+v", err)
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
