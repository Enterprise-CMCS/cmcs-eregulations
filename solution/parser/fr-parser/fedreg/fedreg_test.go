package fedreg

import (
	"testing"
)

func TestFetchContent(t *testing.T) {

}

func TestFetchSection(t *testing.T) {

}

func TestExtractSection(t *testing.T) {
	testTable := []struct {
		Name string
		Input string
		Output string
		Error bool
	}{
		{
			Name: "test-valid",
			Input: "§ 430.12",
			Output: "12",
			Error: false,
		},
		{
			Name: "test-invisible-space",
			Input: "§ㅤ430.11",
			Output: "11",
			Error: false,
		},
		{
			Name: "test-invalid",
			Input: "§ 430",
			Output: "",
			Error: true,
		},
		{
			Name: "test-no-symbol",
			Input: "430.10",
			Output: "10",
			Error: false,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func (t *testing.T) {
			output, err := extractSection(tc.Input)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received (%s)", output)
			}
		})
	}
}
