package main

import (
	"testing"
	"net/http/httptest"
	"net/http"
	"context"
	"time"
	"strings"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/eregs"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/parsexml"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"

	log "github.com/sirupsen/logrus"
	"github.com/go-test/deep"
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
			if diff := deep.Equal(tc.Input, tc.Expected); diff != nil {
				t.Errorf("output not as expected: %+v", diff)
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
/*
	strategy: implement ecfr and eregs mock servers
		1. one valid part version 
		2. one invalid part version
		ecfr endpoints:
			- fetch structure
			- fetch full
		eregs endpoints:
			- post part
			- post supplemental part
	inputs:
		- context
		- thread num (doesn't matter, 1 as default)
		- date (set static, NOT time.now)
		- version structure
	outputs:
		error
		post version struct should match expected output
*/
func TestHandlePartVersion(t *testing.T) {
	log.SetLevel(log.TraceLevel)
	ecfrServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "GET" {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "Expected GET request, received ` + r.Method + `" }`))
			return
		}

		path := strings.Split(r.URL.Path, "/")
		if len(path) < 4 {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "Invalid path length for '` + r.URL.Path + `'" }`))
		} else if path[1] == "structure" {
			//fetch structure
			if path[3] == "title-42.json" {
				w.WriteHeader(http.StatusOK)
				w.Write([]byte(`{
					"identifier": "42",
					"label": "Title 42 - Public Health",
					"label_level": "Title 42",
					"label_description": "Public Health",
					"reserved": false,
					"type": "title",
					"children": [
						{
							"identifier": "IV",
							"label": " Chapter IV - Centers for Medicare &amp; Medicaid Services, Department of Health and Human Services",
							"label_level": " Chapter IV",
							"label_description": "Centers for Medicare &amp; Medicaid Services, Department of Health and Human Services",
							"reserved": false,
							"type": "chapter",
							"children": [
						  		{
									"identifier": "C",
									"label": "Subchapter C - Medical Assistance Programs",
									"label_level": "Subchapter C",
									"label_description": "Medical Assistance Programs",
									"reserved": false,
									"type": "subchapter",
									"children": [
										{
											"identifier": "433",
											"label": "Part 433 - State Fiscal Administration",
											"label_level": "Part 433",
											"label_description": "State Fiscal Administration",
											"reserved": false,
											"type": "part",
											"volumes": [
												"4"
											],
											"children": [
												{
													"identifier": "433.1",
													"label": "§ 433.1 Purpose.",
													"label_level": "§ 433.1",
													"label_description": "Purpose.",
													"reserved": false,
													"type": "section",
													"volumes": [
														"4"
													],
													"received_on": "2017-01-03T00:00:00-0500"
												}
											]
										}
									]
								}
							]
						}
					]
				}`))
			} else if path[3] == "title-43.json" {

			} else {
				w.WriteHeader(http.StatusInternalServerError)
				w.Write([]byte(`{ "exception": "Unrecognized title '` + path[3] + `'" }`))
			}
		} else if path[1] == "full" {
			//fetch full
			if path[3] == "title-42.xml" {
				w.WriteHeader(http.StatusOK)
				w.Write([]byte(`
					<DIV5 N="433" TYPE="PART">
						<HEAD>PART 433 - STATE FISCAL ADMINISTRATION </HEAD>
						<AUTH>
							<HED>Authority:</HED>
							<PSPACE>42 U.S.C. 1302. </PSPACE>
						</AUTH>
						<SOURCE>
							<HED>Source:</HED>
							<PSPACE>43 FR 45201, Sept. 29, 1978, unless otherwise noted. </PSPACE>
						</SOURCE>
						<DIV8 N="433.1" TYPE="SECTION" VOLUME="4">
							<HEAD>§ 433.1 Purpose.</HEAD>
							<P>This part specifies the rates of FFP for services and administration, and prescribes requirements, prohibitions, and FFP conditions relating to State fiscal activities. </P>
						</DIV8>
					</DIV5>
				`))
			} else if path[3] == "title-43.xml" {
	
			} else {
				w.WriteHeader(http.StatusInternalServerError)
				w.Write([]byte(`{ "exception": "Unrecognized title '` + path[3] + `'" }`))
			}
		} else {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "Invalid path '` + r.URL.Path + `'" }`))
		}
	}))
	defer ecfrServer.Close()
	ecfr.EcfrSite = ecfrServer.URL

	eregsServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {

	}))
	defer eregsServer.Close()
	eregs.BaseURL = eregsServer.URL

	testTable := []struct{
		Name string
		Input eregs.Part
		Expected eregs.Part
		Error bool
	}{
		{
			Name: "test-",
			Input: eregs.Part{
				Title: 42,
				Name: "433",
				Date: "2022-01-01",
				Structure: &ecfr.Structure{},
				Document: &parsexml.Part{},
			},
			Expected: eregs.Part{
				Title: 42,
				Name: "433",
				Date: "2022-01-01",
				Structure: &ecfr.Structure{
					Identifier: ecfr.IdentifierString{"42"},
					Label: "Title 42 - Public Health",
					LabelLevel: "Title 42",
					LabelDescription: "Public Health",
					Reserved: false,
					Type: "title",
					Children: []*ecfr.Structure{
						&ecfr.Structure{
							Identifier: ecfr.IdentifierString{"IV"},
							Label: " Chapter IV - Centers for Medicare & Medicaid Services, Department of Health and Human Services",
							LabelLevel: " Chapter IV",
							LabelDescription: "Centers for Medicare &amp; Medicaid Services, Department of Health and Human Services",
							Reserved: false,
							Type: "chapter",
							Children: []*ecfr.Structure{
								&ecfr.Structure{
									Identifier: ecfr.IdentifierString{"C"},
									Label: "Subchapter C - Medical Assistance Programs",
									LabelLevel: "Subchapter C",
									LabelDescription: "Medical Assistance Programs",
									Reserved: false,
									Type: "subchapter",
									Children: []*ecfr.Structure{
										&ecfr.Structure{
											Identifier: ecfr.IdentifierString{"433"},
											Label: "Part 433 - State Fiscal Administration",
											LabelLevel: "Part 433",
											LabelDescription: "State Fiscal Administration",
											Reserved: false,
											Type: "part",
											Children: []*ecfr.Structure{
												&ecfr.Structure{
													Identifier: ecfr.IdentifierString{"433", "1"},
													Label: "§ 433.1 Purpose.",
													LabelLevel: "§ 433.1",
													LabelDescription: "Purpose.",
													Reserved: false,
													Type: "section",
													Children: nil,
													DescendantRange: nil,
												},
											},
											DescendantRange: nil,
										},
									},
									DescendantRange: nil,
								},
							},
							DescendantRange: nil,
						},
					},
					DescendantRange: nil,
				},
				Document: &parsexml.Part{

				},
			},
			Error: false,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			ctx, cancel := context.WithTimeout(context.Background(), 1 * time.Second)
			defer cancel()
			date := time.Date(2022, time.January, 1, 0, 0, 0, 0, time.UTC)
			err := handlePartVersion(ctx, 1, date, &tc.Input)
			diff := deep.Equal(tc.Input.Structure, tc.Expected.Structure)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received (%+v)", tc.Input)
			} else if err == nil && diff != nil {
				t.Errorf("output not as expected: %+v", diff)
			}
		})
	}
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
