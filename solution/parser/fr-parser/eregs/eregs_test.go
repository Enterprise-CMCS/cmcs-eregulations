package eregs

import (
	"testing"

	"github.com/go-test/deep"
)

func TestSendDocument(t *testing.T) {

}

func TestCreateSections(t *testing.T) {
	input := []string{
		"443.42",
		"1.1",
		"443.",
		".42",
		".",
		"",
		"123.45",
	}

	expected := []*Section{
		&Section{
			Title: "42",
			Part: "443",
			Section: "42",
		},
		&Section{
			Title: "42",
			Part: "1",
			Section: "1",
		},
		&Section{
			Title: "42",
			Part: "123",
			Section: "45",
		},
	}

	output := CreateSections("42", input)
	if diff := deep.Equal(expected, output); diff != nil {
		t.Errorf("output not as expected: %+v", diff)
	}
}
