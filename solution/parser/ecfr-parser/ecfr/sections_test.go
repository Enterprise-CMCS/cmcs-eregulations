package ecfr

import (
	"testing"
	"reflect"
)

func TestExtractStructure(t *testing.T) {
	testTable := []struct {
		Name string
	}{
		{
			Name: "test-",
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {

		})
	}
}

func TestExtractSubpart(t *testing.T) {
	testTable := []struct {
		Name string
	}{
		{
			Name: "test-",
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			
		})
	}
}

func TestExtractSection(t *testing.T) {
	input := Structure{
		Identifier: IdentifierString{"432", "1"},
		Label: "§ 432.1 Basis and purpose.",
		LabelLevel: "§ 432.1",
		LabelDescription: "Basis and purpose.",
		Reserved: false,
		Type: "section",
		Children: []*Structure{},
		DescendantRange: RangeString{},
	}

	expected := Section{
		Title: "42",
		Part: "432",
		Section: "1",
	}

	output := extractSection("42", &input)
	if !reflect.DeepEqual(output, expected) {
		t.Errorf("expected (%+v), received (%+v)", expected, output)
	}
}
