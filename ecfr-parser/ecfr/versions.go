package ecfr

import (
	"encoding/json"
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

func ExtractPartVersions(title int, po *partOption) (map[string]struct{}, error) {
	vbody, err := FetchVersions(title, po)
	if err != nil {
		return nil, err
	}
	defer vbody.Close()
	vs := &Versions{}
	d := json.NewDecoder(vbody)
	if err := d.Decode(vs); err != nil {
		return nil, err
	}
	versions := PartVersions(vs.ContentVersions)
	return versions[po.part], nil
}
