package ecfr

import (
	"testing"
	"reflect"
)

func TestRangeStringUnmarshal(t *testing.T) {
	testTable := []struct {
		Name string
		Input []byte
		Expected RangeString
		Error bool
	}{
		{
			Name: "test-valid-rangestring",
			Input: []byte("432.1 – 432.200"),
			Expected: RangeString{"432.1", "432.200"},
			Error: false,
		},
		{
			Name: "test-invalid-rangestring",
			Input: []byte("432.1 – "),
			Expected: RangeString{"432.1"},
			Error: true,
		},
		{
			Name: "test-single-element-rangestring",
			Input: []byte("431.1"),
			Expected: RangeString{"431.1"},
			Error: true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			var rs RangeString
			err := rs.UnmarshalText(tc.Input)
			if err == nil && tc.Error {
				t.Errorf("expected error, received (%+v)", rs)
			} else if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && !reflect.DeepEqual(rs, tc.Expected) {
				t.Errorf("expected (%+v), received (%+v)", tc.Expected, rs)
			}
		})
	}
}

func TestHTMLStringUnmarshal(t *testing.T) {
	
}

func TestIdentifierStringUnmarshal(t *testing.T) {
	
}

func TestSubchapterParts(t *testing.T) {
	
}

func TestExtractSubchapterParts(t *testing.T) {
	
}
