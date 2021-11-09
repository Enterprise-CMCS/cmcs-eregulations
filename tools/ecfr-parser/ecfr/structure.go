package ecfr

import (
	"context"
	"encoding/json"
	"errors"
	"strings"
	"time"
	"html"
)

type Structure struct {
	Identifier       IdentifierString `json:"identifier"`
	Label            HTMLString        `json:"label"`
	LabelLevel       string           `json:"label_level"`
	LabelDescription string           `json:"label_description"`
	Reserved         bool             `json:"reserved"`
	Type             string           `json:"type"`
	Children         []*Structure     `json:"children"`
	DescendantRange  RangeString      `json:"descendant_range"`
}

type RangeString []string

func (rs *RangeString) UnmarshalText(data []byte) error {
	*rs = strings.Split(string(data), " – ")
	return nil
}

type HTMLString string

func (hs *HTMLString) UnmarshalText(data []byte) error {
	*hs = HTMLString(html.UnescapeString(string(data)))
	return nil
}

type IdentifierString []string

func (is *IdentifierString) UnmarshalText(data []byte) error {
	pieces := strings.Split(string(data), ".")
	for _, piece := range pieces {
		*is = append(*is, strings.Split(piece, " ")...)
	}
	return nil
}

var (
	ErrUnexpectedStructure = errors.New("the structure had an unexpected number of children")
)

func SubchapterParts(s *Structure) ([]*Structure, error) {
	if len(s.Children) != 1 {
		return nil, ErrUnexpectedStructure
	}
	if len(s.Children[0].Children) != 1 {
		return nil, ErrUnexpectedStructure
	}
	return s.Children[0].Children[0].Children, nil
}

func ExtractSubchapterParts(ctx context.Context, date time.Time, title int, sub *subchapterOption) ([]string, error) {
	sbody, err := FetchStructure(ctx, date.Format("2006-01-02"), title, sub)
	if err != nil {
		return nil, err
	}
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
