package eregs

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/cmsgov/cmcs-eregulations/lib/ecfr"
	"github.com/cmsgov/cmcs-eregulations/lib/network"
	"github.com/cmsgov/cmcs-eregulations/lib/parsexml"

	log "github.com/sirupsen/logrus"
)

var (
	putPartURL       = "/part"
	existingPartsURL = "/title/%d/versions"
)

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
	UploadRegText   bool            `json:"upload_reg_text"`
	Processed       bool
	UploadLocations bool
}

// ExistingPart is a regulation that has been loaded already
type ExistingPart struct {
	Date     string   `json:"date"`
	PartName []string `json:"part_name"`
}

// PutPart is the function that sends a part to the eRegs server
func PutPart(ctx context.Context, p *Part) (int, error) {
	u, err := parseURL(putPartURL)
	if err != nil {
		return -1, err
	}
	return network.SendJSON(ctx, u, p, true, PostAuth, network.HTTPPut)
}

// GetExistingParts gets existing parts already imported
func GetExistingParts(ctx context.Context, title int) (map[string][]string, int, error) {
	u, err := parseURL(fmt.Sprintf(existingPartsURL, title))
	if err != nil {
		return nil, -1, err
	}

	log.Trace("[eregs] Beginning checking of existing parts for title ", title, " at ", u.String())

	body, code, err := network.Fetch(ctx, u, true, getAuth())
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
