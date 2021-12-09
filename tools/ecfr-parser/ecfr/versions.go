package ecfr

import (
	"context"
	"encoding/json"

	log "github.com/sirupsen/logrus"
)

// Versions is a list of Version structs and is whatis returned by ECFR
type Versions struct {
	ContentVersions []Version `json:"content_versions"`
}

// Version is the struct representing a regulation version from ECFR
type Version struct {
	Date       string
	Identifier string
	Name       string
	Part       string
	Subpart    string
	Title      string
	Type       string
}

// PartVersions breaks an Array of Versions into a map of the correct format.
func PartVersions(versions []Version) map[string]map[string]struct{} {
	result := map[string]map[string]struct{}{}
	for _, version := range versions {
		if result[version.Part] == nil {
			result[version.Part] = map[string]struct{}{}
		}
		// 2016 is unreliable, bump it up to 2017
		if version.Date[0:4] == "2016" {
			version.Date = "2017-01-01"
		}
		result[version.Part][version.Date] = struct{}{}
	}
	return result
}

// ExtractVersions fetches and extracts the necessary information about a specific title
func ExtractVersions(ctx context.Context, title int) (map[string]map[string]struct{}, error) {
	vbody, err := FetchVersions(ctx, title)
	if err != nil {
		return nil, err
	}
	vs := &Versions{}
	d := json.NewDecoder(vbody)
	if err := d.Decode(vs); err != nil {
		log.Trace("[versions] Failed to decode response")
		return nil, err
	}
	versions := PartVersions(vs.ContentVersions)
	return versions, nil
}

// ExtractPartVersions fetches and extracts the necessary information about a specific title and part
func ExtractPartVersions(ctx context.Context, title int, po *PartOption) (map[string]struct{}, error) {
	vbody, err := FetchVersions(ctx, title, po)
	if err != nil {
		return nil, err
	}
	vs := &Versions{}
	d := json.NewDecoder(vbody)
	if err := d.Decode(vs); err != nil {
		return nil, err
	}
	versions := PartVersions(vs.ContentVersions)
	return versions[po.Part], nil
}
