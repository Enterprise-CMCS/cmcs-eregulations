package ecfr

import (
	"context"
	"errors"
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
	s, err := FetchStructure(ctx, date, title, sub)
	if err != nil {
		return nil, err
	}
	partsStructure, err := SubchapterParts(s)
	if err != nil {
		return nil, err
	}
	parts := make([]string, len(partsStructure))
	for i, part := range partsStructure {
		parts[i] = part.Identifier
	}
	return parts, nil
}
