package ecfr

import (
	"context"
	"encoding/json"

	log "github.com/sirupsen/logrus"
)

type Versions struct {
	ContentVersions []Version `json:"content_versions"`
}

type Version struct {
	Date       string
	Identifier string
	Name       string
	Part       string
	Subpart    string
	Title      string
	Type       string
}

func PartVersions(versions []Version) map[string]map[string]struct{} {
	result := map[string]map[string]struct{}{}
	for _, version := range versions {
		if result[version.Part] == nil {
			result[version.Part] = map[string]struct{}{}
		}
		result[version.Part][version.Date] = struct{}{}
	}
	return result
}

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

func ExtractPartVersions(ctx context.Context, title int, po *partOption) (map[string]struct{}, error) {
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
	return versions[po.part], nil
}
