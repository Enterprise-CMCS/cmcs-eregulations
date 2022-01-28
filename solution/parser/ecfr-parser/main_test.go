package main

import (
	"testing"
	"reflect"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/eregs"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/parsexml"

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

func TestParseConfig(t *testing.T) {
	testTable := []struct {
		Name string
		Input eregs.ParserConfig
		Expected eregs.ParserConfig
	}{
		{
			Name: "test-valid-config",
			Input: eregs.ParserConfig{
				Workers: 3,
				Attempts: 4,
				LogLevel: "info",
				UploadSupplemental: true,
				LogParseErrors: false,
				SkipVersions: true,
			},
			Expected: eregs.ParserConfig{
				Workers: 3,
				Attempts: 4,
				LogLevel: "info",
				UploadSupplemental: true,
				LogParseErrors: false,
				SkipVersions: true,
			},
		},
		{
			Name: "test-bad-config",
			Input: eregs.ParserConfig{
				Workers: -1,
				Attempts: -2,
				LogLevel: "warn",
				UploadSupplemental: true,
				LogParseErrors: false,
				SkipVersions: true,
			},
			Expected: eregs.ParserConfig{
				Workers: 1,
				Attempts: 1,
				LogLevel: "warn",
				UploadSupplemental: true,
				LogParseErrors: false,
				SkipVersions: true,
			},
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func (t *testing.T) {
			parseConfig(&tc.Input)
			if !reflect.DeepEqual(tc.Input, tc.Expected) {
				t.Errorf("expected (%+v), received (%+v)", tc.Expected, tc.Input)
			}
			if parsexml.LogParseErrors != tc.Input.LogParseErrors {
				t.Errorf("parsexml.LogParseErrors: expected (%t), received (%t)", tc.Expected.LogParseErrors, parsexml.LogParseErrors)
			}
		})
	}
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

func TestContains(t *testing.T) {
	testTable := []struct {
		Name string
		Array []string
		String string
		Expected bool
	}{
		{
			Name: "test-in-array",
			Array: []string{"aaa", "bbb", "ccc"},
			String: "bbb",
			Expected: true,
		},
		{
			Name: "test-last-element",
			Array: []string{"aaa", "bbb", "ccc"},
			String: "ccc",
			Expected: true,
		},
		{
			Name: "test-not-in-array",
			Array: []string{"aaa", "bbb", "ccc"},
			String: "ddd",
			Expected: false,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			out := contains(tc.Array, tc.String)
			if out != tc.Expected {
				t.Errorf("expected (%t), received (%t)", tc.Expected, out)
			}
		})
	}
}
