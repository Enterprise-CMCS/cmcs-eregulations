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
			[]string{"6", "i", "1"},
			nil,
		},
		{
			"(2) <I>One of the following documents that show a U.S. place of birth and was created at least 5 years before the application for Medicaid.</I> (For children under 16 the document must have been created near the time of birth or 5 years before the date of application.) This document must be one of the following and show a U.S. place of birth",
			[]string{"2"},
			nil,
		},
		{
			"(b) <I>Activities and rates.</I> (1) [Reserved]",
			[]string{"b", "1"},
			nil,
		},
		{
			"(b)<I>Activities and rates.</I>(1)(i) [Reserved]",
			[]string{"b", "1", "i"},
			nil,
		},
		{
			"(b)<I>Activities and rates.</I> -(1) [Reserved]",
			[]string{"b", "1"},
			nil,
		},
		{
			"(b) <I>Activities and rates.</I> - (1) [Reserved]",
			[]string{"b", "1"},
			nil,
		},
		{
			"(b) <I>Activities and rates.</I>-(1) [Reserved]",
			[]string{"b", "1"},
			nil,
		},
		{
			"(c) <I>Filing requirements</I> - (1) <I>Authority to file.</I> - (i) A",
			[]string{"c", "1", "i"},
			nil,
		},
		{
			"(3) <I>Publication of national limits.</I> If CMS determines under this paragraph (h)",
			[]string{"3"},
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
