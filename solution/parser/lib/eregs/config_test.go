package eregs

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/go-test/deep"

	log "github.com/sirupsen/logrus"
)

func TestGetLogLevel(t *testing.T) {
	testTable := []struct {
		Name     string
		Input    string
		Expected log.Level
	}{
		{
			Name:     "test-warn",
			Input:    "warn",
			Expected: log.WarnLevel,
		},
		{
			Name:     "test-fatal",
			Input:    "fatal",
			Expected: log.FatalLevel,
		},
		{
			Name:     "test-error",
			Input:    "error",
			Expected: log.ErrorLevel,
		},
		{
			Name:     "test-info",
			Input:    "info",
			Expected: log.InfoLevel,
		},
		{
			Name:     "test-debug",
			Input:    "debug",
			Expected: log.DebugLevel,
		},
		{
			Name:     "test-trace",
			Input:    "trace",
			Expected: log.TraceLevel,
		},
		{
			Name:     "test-default",
			Input:    "not a valid level",
			Expected: log.WarnLevel,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			out := GetLogLevel(tc.Input)
			if out != tc.Expected {
				t.Errorf("expected (%+v), received (%+v)", tc.Expected, out)
			}
		})
	}
}

func TestRetrieveConfig(t *testing.T) {
	testTable := []struct {
		Name         string
		Server       *httptest.Server
		Output       *ParserConfig
		Error        bool
		ExpectedCode int
	}{
		{
			Name: "test-good-config",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				if r.URL.Path != "/parser_config" {
					w.WriteHeader(http.StatusInternalServerError)
					w.Write([]byte(`{ "exception": "Bad URL ` + r.URL.Path + `!" }`))
				} else {
					w.WriteHeader(http.StatusOK)
					w.Write([]byte(`{
						"workers": 3,
						"retries": 2,
						"loglevel": "info",
						"upload_supplemental_locations": false,
						"log_parse_errors": true,
						"skip_reg_versions": false,
						"parts": [
							{
								"title": 4,
								"type": "subchapter",
								"value": "IV-C",
								"upload_reg_text": true,
								"upload_locations": true
							},
							{
								"title": 5,
								"type": "part",
								"value": "400",
								"upload_reg_text": true,
								"upload_locations": false
							}
						]
					}`))
				}
			})),
			Output: &ParserConfig{
				Workers:            3,
				Retries:            2,
				LogLevel:           "info",
				UploadSupplemental: false,
				LogParseErrors:     true,
				SkipRegVersions:    false,
				SkipFRDocuments:    false,
				Parts: []*PartConfig{
					&PartConfig{
						Title:           4,
						Type:            "subchapter",
						Value:           "IV-C",
						UploadRegText:   true,
						UploadLocations: true,
					},
					&PartConfig{
						Title:           5,
						Type:            "part",
						Value:           "400",
						UploadRegText:   true,
						UploadLocations: false,
					},
				},
			},
			Error:        false,
			ExpectedCode: http.StatusOK,
		},
		{
			Name: "test-bad-response",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusOK)
				w.Write([]byte(`{
					"asdf": 3
					"loglevel": "info",
					"upload_supplemental_locations": false,
					"log_parse_errors" true,
					"skip_reg_versions": false,
					"skip_fr_documents": true,
					"titles": [
						{
							"title": 4,
							"subchapters": "IV-C, IX-D",
							"parts": "123, 456"
						}
						{
							"title": 5,
							"subchapters": "AB-C, DE-F",
							"parts": "789, 101"
						}
					]
				}`))
			})),
			Output:       nil,
			Error:        true,
			ExpectedCode: http.StatusOK,
		},
		{
			Name: "test-bad-fetch",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusInternalServerError)
				w.Write([]byte(`{ "exception": "Expected failure" }`))
			})),
			Output:       nil,
			Error:        true,
			ExpectedCode: http.StatusInternalServerError,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			defer tc.Server.Close()
			BaseURL = tc.Server.URL
			config, code, err := RetrieveConfig()

			diff := deep.Equal(config, tc.Output)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received (%+v)", config)
			} else if err == nil && diff != nil {
				t.Errorf("output not as expected: %+v", diff)
			}

			if code != tc.ExpectedCode {
				t.Errorf("expected code (%d), got (%d)", tc.ExpectedCode, code)
			}
		})
	}
}
