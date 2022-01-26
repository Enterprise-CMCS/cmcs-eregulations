package ecfr

import (
	"testing"
	"reflect"
)

func TestRangeStringUnmarshal(t *testing.T) {
	input := []byte("432.1 – 432.200")
	expected := RangeString{"432.1", "432.200"}
	var rs RangeString
	rs.UnmarshalText(input)
	if !reflect.DeepEqual(rs, expected) {
		t.Errorf("expected (%s), received (%s)", expected, rs)
	}
}

func TestHTMLStringUnmarshal(t *testing.T) {
	input := []byte("&quot;Hello world&quot; &lt;&amp; &#39;")
	expected := HTMLString("\"Hello world\" <& '")
	var hs HTMLString
	hs.UnmarshalText(input)
	if hs != expected {
		t.Errorf("expected (%s), received (%s)", expected, hs)
	}
}

func TestIdentifierStringUnmarshal(t *testing.T) {
	testTable := []struct {
		Name string
		Input []byte
		Expected IdentifierString
	}{
		{
			Name: "test-title-identifier",
			Input: []byte("42"),
			Expected: IdentifierString{"42"},
		},
		{
			Name: "test-chapter-identifier",
			Input: []byte("IV"),
			Expected: IdentifierString{"IV"},
		},
		{
			Name: "test-subchapter-identifier",
			Input: []byte("C"),
			Expected: IdentifierString{"C"},
		},
		{
			Name: "test-part-identifier",
			Input: []byte("430"),
			Expected: IdentifierString{"430"},
		},
		{
			Name: "test-subpart-identifier",
			Input: []byte("A"),
			Expected: IdentifierString{"A"},
		},
		{
			Name: "test-subjectgroup-identifier",
			Input: []byte("ECFR370de681c5a0a70"),
			Expected: IdentifierString{"ECFR370de681c5a0a70"},
		},
		{
			Name: "test-section-identifier",
			Input: []byte("430.1"),
			Expected: IdentifierString{"430", "1"},
		},
		{
			Name: "test-paragraph-identifier",
			Input: []byte("430.1 a 1"),
			Expected: IdentifierString{"430", "1", "a", "1"},
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			var is IdentifierString
			is.UnmarshalText(tc.Input)
			if !reflect.DeepEqual(is, tc.Expected) {
				t.Errorf("expected (%+v), received (%+v)", tc.Expected, is)
			}
		})
	}
}

func TestSubchapterParts(t *testing.T) {
	
}

func TestExtractSubchapterParts(t *testing.T) {
	
}
