package eregs

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"os"
	"path"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/parsexml"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/network"

	log "github.com/sirupsen/logrus"
)

// BaseURL is the URL of the eRegs service that will accept the post requests
var BaseURL string

// SuppContentURL is the URL of the eRegs service that will accept the post request
var SuppContentURL string

var client = &http.Client{
	Transport: &http.Transport{},
}

var partURL  = "/title/%d/existing"

var postAuth = &network.PostAuth{
	Username: os.Getenv("EREGS_USERNAME"),
	Password: os.Getenv("EREGS_PASSWORD"),
}

// Part is the struct used to send a part to the eRegs server
type Part struct {
	Title     int             `json:"title,string" xml:"-"`
	Name      string          `json:"name" xml:"-"`
	Date      string          `json:"date" xml:"-"`
	Structure *ecfr.Structure `json:"structure" xml:"-"`
	Document  *parsexml.Part  `json:"document"`
	Processed bool
}

// ExistingPart is a regulation that has been loaded already
type ExistingPart struct {
	Date     string   `json:"date"`
	PartName []string `json:"partName"`
}

// PostPart is the function that sends a part to the eRegs server
func PostPart(ctx context.Context, p *Part) error {
	eregsPath, err := url.Parse(BaseURL)
	if err != nil {
		return err
	}
	return network.PostJSON(ctx, eregsPath, p, true, postAuth)
}

// PostSupplementalPart is the function that sends a supplemental part to eRegs server
func PostSupplementalPart(ctx context.Context, p ecfr.Part) error {
	eregsPath, err := url.Parse(SuppContentURL)
	if err != nil {
		return err
	}
	return network.PostJSON(ctx, eregsPath, p, true, postAuth)
}

// GetExistingParts gets existing parts already imported
func GetExistingParts(ctx context.Context, title int) (map[string][]string, error) {
	checkURL, err := url.Parse(BaseURL)
	if err != nil {
		return nil, err
	}
	q := checkURL.Query()
	q.Add("json_errors", "true")
	checkURL.RawQuery = q.Encode()
	checkURL.Path = path.Join(checkURL.Path, fmt.Sprintf(partURL, title))

	log.Trace("[eregs] Beginning checking of existing parts for title ", title, " at ", checkURL.String())

	body, err := network.Fetch(ctx, checkURL, true)
	if err != nil {
		return nil, err
	}

	// Cast the body to an array of existing parts
	var vs []ExistingPart
	d := json.NewDecoder(body)
	if err := d.Decode(&vs); err != nil {
		return nil, fmt.Errorf("Unable to decode response body while checking existing versions: %+v", err)
	}

	// reduce the results to the desired format
	result := make(map[string][]string)
	for _, ep := range vs {
		result[ep.Date] = ep.PartName
	}

	return result, nil
}
