package ecfr

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
