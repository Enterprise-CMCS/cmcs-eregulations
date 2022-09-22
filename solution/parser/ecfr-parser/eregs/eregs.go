package eregs

import (
	"context"
	"encoding/json"
	"fmt"
	"net/url"
	"os"
	"path"
	"time"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/network"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/parsexml"

	log "github.com/sirupsen/logrus"
)

// BaseURL is the URL of the eRegs service that will accept the post requests
var BaseURL string

var (
	putPartURL       = "/part"
	parserResultURL  = "/ecfr_parser_result/%d"
	existingPartsURL = "/title/%d/versions"
)

var postAuth = &network.PostAuth{
	Username: os.Getenv("EREGS_USERNAME"),
	Password: os.Getenv("EREGS_PASSWORD"),
}

// Part is the struct used to send a part to the eRegs server
type Part struct {
	Title           int             `json:"title,string" xml:"-"`
	Name            string          `json:"name" xml:"-"`
	Date            string          `json:"date" xml:"-"`
	Structure       *ecfr.Structure `json:"structure" xml:"-"`
	Document        *parsexml.Part  `json:"document"`
	Depth           int             `json:"depth"`
	Sections        []ecfr.Section  `json:"sections"`
	Subparts        []ecfr.Subpart  `json:"subparts"`
	Processed       bool
	UploadLocations bool
}

// ExistingPart is a regulation that has been loaded already
type ExistingPart struct {
	Date     string   `json:"date"`
	PartName []string `json:"part_name"`
}

// ParserResult is the struct used to send results to the eRegs server
type ParserResult struct {
	Title           int    `json:"title,string"`
	Start           string `json:"start"`
	End             string `json:"end"`
	Workers         int    `json:"workers,string"`
	Parts           string `json:"parts"`
	Subchapters     string `json:"subchapters"`
	SkippedVersions int    `json:"skippedVersions,string"`
	TotalVersions   int    `json:"totalVersions,string"`
	Errors          int    `json:"errors,string"`
}

// PutPart is the function that sends a part to the eRegs server
func PutPart(ctx context.Context, p *Part) (int, error) {
	u, err := url.Parse(BaseURL)
	if err != nil {
		return -1, err
	}
	u.Path = path.Join(u.Path, putPartURL)
	return network.SendJSON(ctx, u, p, true, postAuth, network.HTTPPut)
}

// PostParserResult is the function that sends a parser result to the eRegs server
func PostParserResult(ctx context.Context, p *ParserResult) (int, error) {
	u, err := url.Parse(BaseURL)
	if err != nil {
		return -1, err
	}
	u.Path = path.Join(u.Path, fmt.Sprintf(parserResultURL, p.Title))

	p.End = time.Now().Format(time.RFC3339)
	return network.SendJSON(ctx, u, p, true, postAuth, network.HTTPPost)
}

// GetExistingParts gets existing parts already imported
func GetExistingParts(ctx context.Context, title int) (map[string][]string, int, error) {
	u, err := url.Parse(BaseURL)
	if err != nil {
		return nil, -1, err
	}
	u.Path = path.Join(u.Path, fmt.Sprintf(existingPartsURL, title))

	log.Trace("[eregs] Beginning checking of existing parts for title ", title, " at ", u.String())

	body, code, err := network.Fetch(ctx, u, true)
	if err != nil {
		return nil, code, err
	}

	// Cast the body to an array of existing parts
	var vs []ExistingPart
	d := json.NewDecoder(body)
	if err := d.Decode(&vs); err != nil {
		return nil, code, fmt.Errorf("unable to decode response body while checking existing versions: %+v", err)
	}

	// reduce the results to the desired format
	result := make(map[string][]string)
	for _, ep := range vs {
		result[ep.Date] = ep.PartName
	}

	return result, code, nil
}
