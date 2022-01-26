package ecfr

import (
	"testing"
	"reflect"
)

func TestPartVersions(t *testing.T) {
	input := []Version{
		Version{
			Date: "2016-01-01",
			Part: "10",
		},
		Version{
			Date: "2018-01-01",
			Part: "10",
		},
		Version{
			Date: "2019-01-01",
			Part: "10",
		},
		Version{
			Date: "2020-01-01",
			Part: "12",
		},
		Version{
			Date: "2021-01-01",
			Part: "12",
		},
		Version{
			Date: "2022-01-01",
			Part: "10",
		},
	}

	expected := map[string]map[string]struct{}{
		"10": map[string]struct{}{
			"2017-01-01": struct{}{},
			"2018-01-01": struct{}{},
			"2019-01-01": struct{}{},
			"2022-01-01": struct{}{},
		},
		"12": map[string]struct{}{
			"2020-01-01": struct{}{},
			"2021-01-01": struct{}{},
		},
	}

	output := PartVersions(input)

	if !reflect.DeepEqual(output, expected) {
		t.Errorf("expected (%+v), received (%+v)", expected, output)
	}
}

func TestExtractVersions(t *testing.T) {
	
}

func TestExtractPartVersions(t *testing.T) {
	
}
