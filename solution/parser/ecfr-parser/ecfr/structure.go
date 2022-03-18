package ecfr

import (
	"context"
	"encoding/json"
	"errors"
	"html"
	"strings"
	"time"
)

// Structure is the struct that represents the structure of a regulation part at eCFR
type Structure struct {
	Identifier       IdentifierString `json:"identifier"`
	Label            HTMLString       `json:"label"`
	LabelLevel       string           `json:"label_level"`
	LabelDescription string           `json:"label_description"`
	Reserved         bool             `json:"reserved"`
	Type             string           `json:"type"`
	Children         []*Structure     `json:"children"`
	DescendantRange  RangeString      `json:"descendant_range"`
}

// RangeString is just an array of strings but required for the JSON unmarshalling
type RangeString []string

// UnmarshalJSON splits the string into parts or populates an array or object (if it is one)
func (rs *RangeString) UnmarshalJSON(data []byte) error {
	s := string(data)
	if len(s) > 0 && (strings.HasPrefix(s, "[") || strings.HasPrefix(s, "{")) {
		json.Unmarshal(data, *rs)
	} else {
		*rs = strings.Split(s, " – ")
	}
	return nil
}

// HTMLString is just a string used for JSON unmarshalling
type HTMLString string

// UnmarshalText escapes the response from eCFR correctly to prevent "&amp" from showing
func (hs *HTMLString) UnmarshalText(data []byte) error {
	*hs = HTMLString(html.UnescapeString(string(data)))
	return nil
}

// IdentifierString is just an array of strings but required for the JSON unmarshalling
type IdentifierString []string

// UnmarshalJSON splits a string into parts, or populates an array or object (if it is one)
func (is *IdentifierString) UnmarshalJSON(data []byte) error {
	s := string(data)
	if len(s) > 0 && (strings.HasPrefix(s, "[") || strings.HasPrefix(s, "{")) {
		json.Unmarshal(data, *is)
	} else {
		pieces := strings.Split(s, ".")
		for _, piece := range pieces {
			*is = append(*is, strings.Split(piece, " ")...)
		}
	}
	return nil
}

var (
    // ErrUnexpectedStructure is an error for when the structure does not appear to be formatted correctly
	ErrUnexpectedStructure = errors.New("the structure had an unexpected number of children")
)

// SubchapterParts breaks down a Structure into an array of Structures
func SubchapterParts(s *Structure) ([]*Structure, error) {
	if len(s.Children) != 1 {
		return nil, ErrUnexpectedStructure
	}
	if len(s.Children[0].Children) != 1 {
		return nil, ErrUnexpectedStructure
	}
	return s.Children[0].Children[0].Children, nil
}

// ExtractSubchapterParts extracts the subchapter parts from eCFR and returns then as an array of strings
func ExtractSubchapterParts(ctx context.Context, date time.Time, title int, sub *SubchapterOption) ([]string, error) {
	sbody, _, err := FetchStructure(ctx, date.Format("2006-01-02"), title, sub)
	if err != nil {
		return nil, err
	}
	s := &Structure{}
	sd := json.NewDecoder(sbody)
	if err := sd.Decode(s); err != nil {
		return nil, err
	}
	partsStructure, err := SubchapterParts(s)
	if err != nil {
		return nil, err
	}
	parts := make([]string, len(partsStructure))
	for i, part := range partsStructure {
		parts[i] = part.Identifier[0]
	}
	return parts, nil
}
