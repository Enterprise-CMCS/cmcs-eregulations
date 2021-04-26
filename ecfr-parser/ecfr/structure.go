package ecfr

import (
	"time"
)

type Structure struct {
	Identifier       string       `json:"identifier"`
	Label            string       `json:"label"`
	LabelLevel       string       `json:"label_level"`
	LabelDescription string       `json:"label_description"`
	Reserved         bool         `json:"reserved"`
	Type             string       `json:"type"`
	Children         []*Structure `json:"children"`
}

func SubchapterParts(s *Structure) []*Structure {
	return s.Children[0].Children[0].Children
}

func ExtractSubchapterParts(date time.Time, title int, sub *subchapterOption) ([]string, error) {
	s, err := FetchStructure(date, title, sub)
	if err != nil {
		return nil, err
	}
	partsStructure := SubchapterParts(s)
	parts := make([]string, len(partsStructure))
	for i, part := range partsStructure {
		parts[i] = part.Identifier
	}
	return parts, nil
}
