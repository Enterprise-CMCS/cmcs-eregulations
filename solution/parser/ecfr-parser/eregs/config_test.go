package eregs

import (
	"testing"
)

func TestSubchapterArgString(t *testing.T) {
	arg := SubchapterArg{"one", "two"}
	if arg.String() != "one-two" {
		t.Errorf("expected (%s), got (%s)", "one-two", arg.String())
	}
}

func TestSubchapterArgSet(t *testing.T) {
	testTable := []struct {
		Name string
		Input string
		Error bool
	}{
		{
			Name: "test-single-arg",
			Input: "one",
			Error: true,
		},
		{
			Name: "test-two-args",
			Input: "one-two",
			Error: false,
		},
		{
			Name: "test-bad-args",
			Input: "onetwo*three/-",
			Error: true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			arg := SubchapterArg{}
			err := arg.Set(tc.Input)
			if err == nil && tc.Error {
				t.Errorf("expected error, none received")
			} else if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && arg.String() != tc.Input {
				t.Errorf("expected (%s), got (%s)", tc.Input, arg.String())
			}
		})
	}
}

func TestSubchapterList(t *testing.T) {
	
}

func TestPartList(t *testing.T) {
	
}

func TestRetrieveConfig(t *testing.T) {
	
}
