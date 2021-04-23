package ecfr

import (
	"encoding/json"
	"time"
)

type Structure struct {
	Identifier       string
	Label            string
	LabelLevel       string `json:"label_level"`
	LabelDescription string `json:"label_discription"`
	Reserved         bool
	Type             string
	Children         []*Structure
}

func SubchapterParts(s *Structure) []*Structure {
	return s.Children[0].Children[0].Children
}

func ExtractSubchapterParts(date time.Time, title int, chapter, subchapter string) ([]*Structure, error) {
	sbody, err := FetchStructure(date, title, Subchapter(subchapter, chapter))
	if err != nil {
		return nil, err
	}
	defer sbody.Close()
	s := &Structure{}
	sd := json.NewDecoder(sbody)
	if err := sd.Decode(s); err != nil {
		return nil, err
	}
	parts := SubchapterParts(s)
	return parts, nil
}
