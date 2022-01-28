package parsexml

import (
	"reflect"
	"testing"
)

func TestGenerateParagraphCitation(t *testing.T) {
	testTable := []struct {
		Name string
		Paragraph *Paragraph
		Previous *Paragraph
		Expected []string
		Error bool
	}{
		{
			Name: "test-1-level",
			Paragraph: &Paragraph{
				Type: "Paragraph",
				Content: "(a) <I>Basis, purpose, and definitions.</I> (1) This section implements...",
				Citation: []string{"a", "1"},
				Marker: []string{"a", "1"},
			},
			Previous: nil,
			Expected: []string{"a", "1"},
			Error: false,
		},
		{
			Name: "test-2-levels",
			Paragraph: &Paragraph{
				Type: "Paragraph",
				Content: "(2) For purposes of this part -",
				Citation: []string{},
				Marker: []string{},
			},
			Previous: &Paragraph{
				Type: "Paragraph",
				Content: "(a) <I>Basis, purpose, and definitions.</I> (1) This section implements...",
				Citation: []string{"a", "1"},
				Marker: []string{"a", "1"},
			},
			Expected: []string{"a", "2"},
			Error: false,
		},
		{
			Name: "test-3-levels",
			Paragraph: &Paragraph{
				Type: "Paragraph",
				Content: "(iii) Any comments from the Governor must be submitted to CMS with the...",
				Citation: []string{},
				Marker: []string{},
			},
			Previous: &Paragraph{
				Type: "Paragraph",
				Content: "(ii) The plan must provide that the Governor will be given a specific period...",
				Citation: []string{"b", "1", "ii"},
				Marker: []string{"ii"},
			},
			Expected: []string{"b", "1", "iii"},
			Error: false,
		},
		{
			Name: "test-4-levels",
			Paragraph: &Paragraph{
				Type: "Paragraph",
				Content: "(B) Federally protected rights regarding off-reservation hunting, fishing...",
				Citation: []string{},
				Marker: []string{},
			},
			Previous: &Paragraph{
				Type: "Paragraph",
				Content: "(A) Rights of ownership or possession in any lands described in paragraph ...",
				Citation: []string{"e", "3", "iii", "A"},
				Marker: []string{"A"},
			},
			Expected: []string{"e", "3", "iii", "B"},
			Error: false,
		},
		{
			Name: "test-empty-previous-citation",
			Paragraph: &Paragraph{
				Type: "Paragraph",
				Content: "(viii) <I>Basis, purpose, and definitions.</I> (1) This section implements...",
				Citation: []string{"a", "1"},
				Marker: []string{"a", "1"},
			},
			Previous: &Paragraph{
				Type: "Paragraph",
				Content: "(2) For purposes of this part -",
				Citation: []string{},
				Marker: []string{},
			},
			Expected: nil,
			Error: false,
		},
		{
			Name: "test-zero-length-marker",
			Paragraph: &Paragraph{
				Type: "Paragraph",
				Content: "nothing",
				Citation: []string{},
				Marker: []string{},
			},
			Previous: nil,
			Expected: []string{},
			Error: false,
		},
		{
			Name: "test-letter-vs-roman",
			Paragraph: &Paragraph{
				Type: "Paragraph",
				Content: "(i) <I>Eligibility based on incurred medical expenses.</I> (1) Whether a State elects...",
				Citation: []string{},
				Marker: []string{},
			},
			Previous: &Paragraph{
				Type: "Paragraph",
				Content: "(3) <I>Chronological order by bill submission date.</I> Under this option, the agency...",
				Citation: []string{"h", "3"},
				Marker: []string{"3"},
			},
			Expected: []string{"i", "1"},
			Error: false,
		},
		{
			Name: "test-letter-vs-roman-i",
			Paragraph: &Paragraph{
				Type: "Paragraph",
				Content: "(i) The agency must execute written agreements with other agencies before releasing...",
				Citation: []string{},
				Marker: []string{},
			},
			Previous: &Paragraph{
				Type: "Paragraph",
				Content: "(h) Information exchanged electronically between the State Medicaid agency and any...",
				Citation: []string{"h"},
				Marker: []string{"h"},
			},
			Expected: []string{"i"},
			Error: false,
		},
		{
			Name: "test-letter-vs-roman-v-1",
			Paragraph: &Paragraph{
				Type: "Paragraph",
				Content: "(v) <I>Applicability date.</I> Sections 438.3(h) and (q) apply to the rating...",
				Citation: []string{},
				Marker: []string{},
			},
			Previous: &Paragraph{
				Type: "Paragraph",
				Content: "(u) <I>Recordkeeping requirements.</I> MCOs, PIHPs, and PAHPs must retain, and...",
				Citation: []string{"u"},
				Marker: []string{"u"},
			},
			Expected: []string{"v"},
			Error: false,
		},
		{
			Name: "test-letter-vs-roman-v-2",
			Paragraph: &Paragraph{
				Type: "Paragraph",
				Content: "(v) <I>Applicability date.</I> Sections 438.3(h) and (q) apply to the rating...",
				Citation: []string{},
				Marker: []string{},
			},
			Previous: &Paragraph{
				Type: "Paragraph",
				Content: "(u) <I>Recordkeeping requirements.</I> MCOs, PIHPs, and PAHPs must retain, and...",
				Citation: []string{"u", "v", "w"},
				Marker: []string{"u"},
			},
			Expected: []string{"v"},
			Error: false,
		},
		{
			Name: "test-wrong-paragraph-order",
			Paragraph: &Paragraph{
				Type: "Paragraph",
				Content: "(iv) Individuals whose eligibility was determined under a State's option under...",
				Citation: []string{},
				Marker: []string{},
			},
			Previous: &Paragraph{
				Type: "Paragraph",
				Content: "(b) <I>Negative case reviews.</I> Except as provided in paragraph (c) of this...",
				Citation: []string{"b"},
				Marker: []string{"b"},
			},
			Expected: nil,
			Error: true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			out, err := generateParagraphCitation(tc.Paragraph, tc.Previous)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received (%+v)", out)
			} else if err == nil && !reflect.DeepEqual(out, tc.Expected) {
				t.Errorf("expected (%+v), received (%+v)", tc.Expected, out)
			}
		})
	}
}

func TestMatchLabelType(t *testing.T) {
	testTable := []struct {
		Name string
		Input string
		Expected int
	}{
		{
			Name: "test-alpha",
			Input: "a",
			Expected: 0,
		},
		{
			Name: "test-num",
			Input: "123",
			Expected: 1,
		},
		{
			Name: "test-roman-1",
			Input: "ix",
			Expected: 2,
		},
		{
			Name: "test-roman-2",
			Input: "viii",
			Expected: 2,
		},
		{
			Name: "test-upper",
			Input: "A",
			Expected: 3,
		},
		{
			Name: "test-italic-num",
			Input: "<I>123</I>",
			Expected: 4,
		},
		{
			Name: "test-italic-roman-1",
			Input: "<I>ix</I>",
			Expected: 5,
		},
		{
			Name: "test-italic-roman-2",
			Input: "<I>viii</I>",
			Expected: 5,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			out := matchLabelType(tc.Input)
			if out != tc.Expected {
				t.Errorf("expected (%d), received (%d)", tc.Expected, out)
			}
		})
	}
}

func TestExtractMarker(t *testing.T) {
	tests := []struct {
		Input    string
		Expected []string
	}{
		{
			"(a)",
			[]string{"a"},
		},
		{
			"(6)(i)",
			[]string{"6", "i"},
		},
		{
			"(6)(i)(1)",
			[]string{"6", "i", "1"},
		},
		{
			"(2) <I>One of the following documents that show a U.S. place of birth and was created at least 5 years before the application for Medicaid.</I> (For children under 16 the document must have been created near the time of birth or 5 years before the date of application.) This document must be one of the following and show a U.S. place of birth",
			[]string{"2"},
		},
		{
			"(b) <I>Activities and rates.</I> (1) [Reserved]",
			[]string{"b", "1"},
		},
		{
			"(b)<I>Activities and rates.</I>(1)(i) [Reserved]",
			[]string{"b", "1", "i"},
		},
		{
			"(b)<I>Activities and rates.</I> -(1) [Reserved]",
			[]string{"b", "1"},
		},
		{
			"(b) <I>Activities and rates.</I> - (1) [Reserved]",
			[]string{"b", "1"},
		},
		{
			"(b) <I>Activities and rates.</I>-(1) [Reserved]",
			[]string{"b", "1"},
		},
		{
			"(c) <I>Filing requirements</I> - (1) <I>Authority to file.</I> - (i) A",
			[]string{"c", "1", "i"},
		},
		{
			"(3) <I>Publication of national limits.</I> If CMS determines under this paragraph (h)",
			[]string{"3"},
		},
		{
			"(<I>1</I>) A copy of the disallowance letter. ",
			[]string{"<I>1</I>"},
		},
		{
			"(<I>ix</I>) A copy of the disallowance letter. ",
			[]string{"<I>ix</I>"},
		},
		{
			"nothing",
			nil,
		},
	}
	for _, test := range tests {
		result := extractMarker(test.Input)
		if !reflect.DeepEqual(result, test.Expected) {
			t.Errorf("unexpected result, got %+v, expected %+v", result, test.Expected)
		}
	}
}
