package api

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/go-test/deep"
)

func TestSubchapterArgString(t *testing.T) {
	arg := SubchapterArg{"one", "two"}
	expected := "one-two"
	if arg.String() != expected {
		t.Errorf("expected (%s), got (%s)", expected, arg.String())
	}
}

func TestSubchapterArgSet(t *testing.T) {
	testTable := []struct {
		Name  string
		Input string
		Error bool
	}{
		{
			Name:  "test-single-arg",
			Input: "one",
			Error: true,
		},
		{
			Name:  "test-two-args",
			Input: "one-two",
			Error: false,
		},
		{
			Name:  "test-bad-args",
			Input: "one-",
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

func TestSubchapterListUnmarshalText(t *testing.T) {
	testTable := []struct {
		Name   string
		Input  []byte
		Output *SubchapterList
		Error  bool
	}{
		{
			Name:  "test-single-good",
			Input: []byte("IV-C"),
			Output: &SubchapterList{
				SubchapterArg{"IV", "C"},
			},
			Error: false,
		},
		{
			Name:  "test-multi-good",
			Input: []byte("IV-C, AB-C, EF-G"),
			Output: &SubchapterList{
				SubchapterArg{"IV", "C"},
				SubchapterArg{"AB", "C"},
				SubchapterArg{"EF", "G"},
			},
			Error: false,
		},
		{
			Name:  "test-inconsistent-spacing",
			Input: []byte("IV-C, AB-C,EF-G"),
			Output: &SubchapterList{
				SubchapterArg{"IV", "C"},
				SubchapterArg{"AB", "C"},
				SubchapterArg{"EF", "G"},
			},
			Error: false,
		},
		{
			Name:   "test-first-arg-bad",
			Input:  []byte("IV"),
			Output: nil,
			Error:  true,
		},
		{
			Name:   "test-second-arg-bad",
			Input:  []byte("-C"),
			Output: nil,
			Error:  true,
		},
		{
			Name:   "test-empty-args",
			Input:  []byte("-"),
			Output: nil,
			Error:  true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			var sl SubchapterList
			err := sl.UnmarshalText(tc.Input)

			diff := deep.Equal(&sl, tc.Output)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received (%+v)", sl)
			} else if err == nil && diff != nil {
				t.Errorf("output not as expected: %+v", diff)
			}
		})
	}
}

func TestPartListUnmarshalText(t *testing.T) {
	testTable := []struct {
		Name   string
		Input  []byte
		Output *PartList
	}{
		{
			Name:   "test-single-good",
			Input:  []byte("123"),
			Output: &PartList{"123"},
		},
		{
			Name:   "test-multi-good",
			Input:  []byte("123, 456, 789"),
			Output: &PartList{"123", "456", "789"},
		},
		{
			Name:   "test-inconsistent-spacing",
			Input:  []byte("123, 456,789"),
			Output: &PartList{"123", "456", "789"},
		},
		{
			Name:   "test-invalid-middle-number",
			Input:  []byte("123, a, 456"),
			Output: &PartList{"123", "456"},
		},
		{
			Name:   "test-single-letter",
			Input:  []byte("a"),
			Output: &PartList{},
		},
		{
			Name:   "test-bad-number",
			Input:  []byte("12a3"),
			Output: &PartList{},
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			var pl PartList
			pl.UnmarshalText(tc.Input)

			if diff := deep.Equal(&pl, tc.Output); diff != nil {
				t.Errorf("output not as expected: %+v", diff)
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
						"titles": [
							{
								"title": 4,
								"subchapters": "IV-C, IX-D",
								"parts": "123, 456"
							},
							{
								"title": 5,
								"subchapters": "AB-C, DE-F",
								"parts": "789, 101"
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
				Titles: []*TitleConfig{
					&TitleConfig{
						Title: 4,
						Subchapters: SubchapterList{
							SubchapterArg{"IV", "C"},
							SubchapterArg{"IX", "D"},
						},
						Parts: PartList{"123", "456"},
					},
					&TitleConfig{
						Title: 5,
						Subchapters: SubchapterList{
							SubchapterArg{"AB", "C"},
							SubchapterArg{"DE", "F"},
						},
						Parts: PartList{"789", "101"},
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
