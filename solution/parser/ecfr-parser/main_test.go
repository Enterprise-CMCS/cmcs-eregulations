package main

import (
	"testing"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/eregs"

	log "github.com/sirupsen/logrus"
)

func TestInit(t *testing.T) {
	if eregs.BaseURL != DefaultBaseURL {
		t.Errorf("eregs.BaseURL: expected (%s), received (%s)", DefaultBaseURL, eregs.BaseURL)
	}
}

func TestGetLogLevel(t *testing.T) {
	testTable := []struct {
		Name string
		Input string
		Expected log.Level
	}{
		{
			Name: "test-warn",
			Input: "warn",
			Expected: log.WarnLevel,
		},
		{
			Name: "test-fatal",
			Input: "fatal",
			Expected: log.FatalLevel,
		},
		{
			Name: "test-error",
			Input: "error",
			Expected: log.ErrorLevel,
		},
		{
			Name: "test-info",
			Input: "info",
			Expected: log.InfoLevel,
		},
		{
			Name: "test-debug",
			Input: "debug",
			Expected: log.DebugLevel,
		},
		{
			Name: "test-trace",
			Input: "trace",
			Expected: log.TraceLevel,
		},
		{
			Name: "test-default",
			Input: "not a valid level",
			Expected: log.WarnLevel,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func (t *testing.T) {
			out := getLogLevel(tc.Input)
			if out != tc.Expected {
				t.Errorf("expected (%+v), received (%+v)", tc.Expected, out)
			}
		})
	}
}

//NOT IMPLEMENTED
func TestParseConfig(t *testing.T) {
	
}

//NOT IMPLEMENTED
//SHOULD NOT TEST IF POSSIBLE
func TestLambdaHandler(t *testing.T) {
	
}

//NOT IMPLEMENTED
//SHOULD NOT TEST IF POSSIBLE
func TestMainFunction(t *testing.T) {
	
}

//NOT IMPLEMENTED
func TestStart(t *testing.T) {
	
}

//NOT IMPLEMENTED
func TestParseTitle(t *testing.T) {
	
}

//NOT IMPLEMENTED
func TestStartHandlePartVersionWorker(t *testing.T) {
	
}

//NOT IMPLEMENTED
func TestHandlePartVersion(t *testing.T) {
	
}

//NOT IMPLEMENTED
func TestContains(t *testing.T) {
	
}
