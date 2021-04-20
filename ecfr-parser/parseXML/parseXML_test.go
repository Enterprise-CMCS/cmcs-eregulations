package parseXML

import (
	"reflect"
	"testing"
)

func TestExtractParagraphMarker(t *testing.T) {
	tests := []struct {
		input  string
		output []string
		err    error
	}{
		{
			"(a)",
			[]string{"a"},
			nil,
		},
		{
			"(6)(i)",
			[]string{"6", "i"},
			nil,
		},
		{
			"(6)(i)(1)",
			[]string{"6", "i"},
			nil,
		},
		{
			"(b) <I>Activities and rates.</I> (1) [Reserved]",
			[]string{"b", "1"},
			nil,
		},
		{
			"(b)<I>Activities and rates.</I>(1) [Reserved]",
			[]string{"b", "1"},
			nil,
		},
	}
	for _, test := range tests {
		result, err := extractMarker(test.input)
		if err != test.err {
			t.Errorf("unexpected error, got %s, expected %s", err, test.err)
		}
		if !reflect.DeepEqual(result, test.output) {
			t.Errorf("unexpected result, got %+v, expected %+v", result, test.output)
		}
	}
}
