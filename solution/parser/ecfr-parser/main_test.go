package main

import (
	"container/list"
	"context"
	"encoding/json"
	"encoding/xml"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/cmsgov/cmcs-eregulations/lib/ecfr"
	"github.com/cmsgov/cmcs-eregulations/lib/eregs"
	"github.com/cmsgov/cmcs-eregulations/lib/parsexml"

	"github.com/go-test/deep"
)

func Run(t *testing.T, name string, f func(*testing.T)) bool {
	config = &eregs.ParserConfig{
		Workers:            3,
		LogLevel:           "trace",
		UploadSupplemental: true,
		LogParseErrors:     true,
		SkipRegVersions:    true,
		SkipFRDocuments:    true,
		Titles: []*eregs.TitleConfig{
			&eregs.TitleConfig{
				Title: 42,
				Subchapters: eregs.SubchapterList{
					eregs.SubchapterArg{"IV", "C"},
				},
				Parts: eregs.PartList{"400", "457", "460"},
			},
			&eregs.TitleConfig{
				Title: 43,
				Subchapters: eregs.SubchapterList{
					eregs.SubchapterArg{"AB", "C"},
				},
				Parts: eregs.PartList{"1", "2", "3"},
			},
		},
	}

	return t.Run(name, f)
}

func TestParseConfig(t *testing.T) {
	testTable := []struct {
		Name     string
		Input    eregs.ParserConfig
		Expected eregs.ParserConfig
	}{
		{
			Name: "test-valid-config",
			Input: eregs.ParserConfig{
				Workers:            3,
				Retries:            3,
				LogLevel:           "info",
				UploadSupplemental: true,
				LogParseErrors:     false,
				SkipRegVersions:    true,
				SkipFRDocuments:    true,
			},
			Expected: eregs.ParserConfig{
				Workers:            3,
				Retries:            3,
				LogLevel:           "info",
				UploadSupplemental: true,
				LogParseErrors:     false,
				SkipRegVersions:    true,
				SkipFRDocuments:    true,
			},
		},
		{
			Name: "test-bad-config",
			Input: eregs.ParserConfig{
				Workers:            -1,
				Retries:            -1,
				LogLevel:           "warn",
				UploadSupplemental: true,
				LogParseErrors:     false,
				SkipRegVersions:    true,
				SkipFRDocuments:    true,
			},
			Expected: eregs.ParserConfig{
				Workers:            1,
				Retries:            0,
				LogLevel:           "warn",
				UploadSupplemental: true,
				LogParseErrors:     false,
				SkipRegVersions:    true,
				SkipFRDocuments:    true,
			},
		},
	}

	for _, tc := range testTable {
		Run(t, tc.Name, func(t *testing.T) {
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

func TestStart(t *testing.T) {
	eregsServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "GET" {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "Expected GET request!" }`))
		} else if r.URL.Path == "/parser_config" {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte(`{
				"workers": 3,
				"retries": 3,
				"loglevel": "trace",
				"upload_supplemental_locations": true,
				"log_parse_errors": false,
				"skip_reg_versions": false,
				"skip_fr_documents": true,
				"titles": [
					{
						"title": 42,
						"subchapters": "IV-C",
						"parts": "400, 457, 460"
					},
					{
						"title": 43,
						"subchapters": "AB-C",
						"parts": "1, 2, 3"
					},
					{
						"title": 44,
						"subchapters": "XY-Z",
						"parts": "4, 5, 6"
					}
				]
			}`))
		} else {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "Invalid path '` + r.URL.Path + `'" }`))
		}
	}))
	defer eregsServer.Close()
	eregs.BaseURL = eregsServer.URL

	parseFailures := 0

	testTable := []struct {
		Name               string
		ParseTitlesFunc    func() error
		RetrieveConfigFunc func() (*eregs.ParserConfig, int, error)
		Error              bool
	}{
		{
			Name: "test-success",
			ParseTitlesFunc: func() error {
				return nil
			},
			RetrieveConfigFunc: func() (*eregs.ParserConfig, int, error) {
				return eregs.RetrieveConfig()
			},
			Error: false,
		},
		{
			Name: "test-retrieve-config-failure",
			ParseTitlesFunc: func() error {
				return nil
			},
			RetrieveConfigFunc: func() (*eregs.ParserConfig, int, error) {
				return nil, -1, fmt.Errorf("failed to retrieve config")
			},
			Error: true,
		},
		{
			Name: "test-parse-titles-failure",
			ParseTitlesFunc: func() error {
				return fmt.Errorf("titles failed to parse")
			},
			RetrieveConfigFunc: func() (*eregs.ParserConfig, int, error) {
				return eregs.RetrieveConfig()
			},
			Error: true,
		},
		{
			Name: "test-parse-titles-retry",
			ParseTitlesFunc: func() error {
				if parseFailures > 1 {
					return nil
				}
				parseFailures++
				return fmt.Errorf("failed to parse titles")
			},
			RetrieveConfigFunc: func() (*eregs.ParserConfig, int, error) {
				return eregs.RetrieveConfig()
			},
			Error: false,
		},
	}

	for _, tc := range testTable {
		Run(t, tc.Name, func(t *testing.T) {
			ParseTitlesFunc = tc.ParseTitlesFunc
			RetrieveConfigFunc = tc.RetrieveConfigFunc
			err := start()
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received none")
			}
		})
	}
}

func TestParseTitles(t *testing.T) {
	testTable := []struct {
		Name               string
		ParseTitleFunc     func(*eregs.TitleConfig) error
		RetrieveConfigFunc func() (*eregs.ParserConfig, int, error)
		Error              bool
	}{
		{
			Name: "test-success",
			ParseTitleFunc: func(title *eregs.TitleConfig) error {
				return nil
			},
			Error: false,
		},
		{
			Name: "test-parse-title-failure",
			ParseTitleFunc: func(title *eregs.TitleConfig) error {
				return fmt.Errorf("something bad happened")
			},
			Error: true,
		},
	}

	for _, tc := range testTable {
		Run(t, tc.Name, func(t *testing.T) {
			ParseTitleFunc = tc.ParseTitleFunc
			err := parseTitles()
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received none")
			}
		})
	}
}

func TestParseTitle(t *testing.T) {
	SleepFunc = func(t time.Duration) {}

	ecfrServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "GET" {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "Expected GET request, received ` + r.Method + `" }`))
			return
		}

		path := strings.Split(r.URL.Path, "/")
		if len(path) < 3 {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "Invalid path length '` + r.URL.Path + `'" }`))
			return
		}

		if path[1] == "structure" {
			//fetch structure
			chapter, ok := r.URL.Query()["chapter"]
			if !ok || len(chapter[0]) < 1 {
				w.WriteHeader(http.StatusInternalServerError)
				w.Write([]byte(`{ "exception": "chapter missing`))
				return
			}
			subchapter, ok := r.URL.Query()["subchapter"]
			if !ok || len(chapter[0]) < 1 {
				w.WriteHeader(http.StatusInternalServerError)
				w.Write([]byte(`{ "exception": "subchapter missing`))
				return
			}

			if string(chapter[0]) == "IV" && string(subchapter[0]) == "C" {
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
				return
			}
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "No such chapter subchapter combo" }`))
			return
		} else if path[1] == "versions" {
			if path[2] == "title-42" {
				w.WriteHeader(http.StatusOK)
				w.Write([]byte(`{
					"content_versions": [
						{
							"date": "2018-01-01",
							"identifier": "433.1",
							"name": "§ 433.1 Purpose.",
							"part": "433",
							"removed": false,
							"title": "42",
							"type": "section"
						},
						{
							"date": "2019-01-01",
							"identifier": "433.1",
							"name": "§ 433.1 Purpose.",
							"part": "433",
							"removed": false,
							"title": "42",
							"type": "section"
						},
						{
							"date": "2020-01-01",
							"identifier": "433.1",
							"name": "§ 433.1 Purpose.",
							"part": "433",
							"removed": false,
							"title": "42",
							"type": "section"
						}
					]
				}`))
			} else {
				w.WriteHeader(http.StatusInternalServerError)
				w.Write([]byte(`{ "exception": "No such title to get versions for" }`))
			}
		} else {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "Invalid path '` + r.URL.Path + `'" }`))
		}
	}))
	defer ecfrServer.Close()
	ecfr.EcfrSite = ecfrServer.URL

	eregsServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "GET" {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "Expected GET request, received ` + r.Method + `" }`))
			return
		}

		if r.URL.Path == "/title/42/versions" {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte(`[
				{
					"date": "2019-01-01",
					"part_name": [
						"433"
					]
				}
			]`))
		} else {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "Unrecognized path" }`))
			return
		}
	}))
	defer eregsServer.Close()
	eregs.BaseURL = eregsServer.URL

	var WorkerFunc func(*eregs.Part)

	StartVersionWorkerFunc = func(ctx context.Context, thread int, ch chan *list.List, wg *sync.WaitGroup) {
		for versionList := range ch {
			for versionElement := versionList.Front(); versionElement != nil; versionElement = versionElement.Next() {
				version := versionElement.Value.(*eregs.Part)
				WorkerFunc(version)
			}
		}
		wg.Done()
	}

	testTable := []struct {
		Name       string
		WorkerFunc func(*eregs.Part)
		Input      eregs.TitleConfig
		Error      bool
	}{
		{
			Name: "test-valid",
			WorkerFunc: func(version *eregs.Part) {
				version.Processed = true
			},
			Input: eregs.TitleConfig{
				Title: 42,
				Subchapters: eregs.SubchapterList{
					eregs.SubchapterArg{"IV", "C"},
				},
				Parts: eregs.PartList{"1", "2", "3"},
			},
			Error: false,
		},
		{
			Name: "test-process-fail",
			WorkerFunc: func(version *eregs.Part) {
				version.Processed = false
			},
			Input: eregs.TitleConfig{
				Title: 42,
				Subchapters: eregs.SubchapterList{
					eregs.SubchapterArg{"IV", "C"},
				},
				Parts: eregs.PartList{"1", "2", "3"},
			},
			Error: true,
		},
		{
			Name: "test-no-parts",
			WorkerFunc: func(version *eregs.Part) {
				version.Processed = false
			},
			Input: eregs.TitleConfig{
				Title:       42,
				Subchapters: eregs.SubchapterList{},
				Parts:       eregs.PartList{},
			},
			Error: true,
		},
		{
			Name: "test-no-parts",
			WorkerFunc: func(version *eregs.Part) {
				version.Processed = true
			},
			Input: eregs.TitleConfig{
				Title:       42,
				Subchapters: eregs.SubchapterList{},
				Parts:       eregs.PartList{},
			},
			Error: true,
		},
		{
			Name:       "test-no-toc",
			WorkerFunc: func(version *eregs.Part) {},
			Input: eregs.TitleConfig{
				Title: 43,
				Subchapters: eregs.SubchapterList{
					eregs.SubchapterArg{"IV", "C"},
				},
				Parts: eregs.PartList{"433"},
			},
			Error: true,
		},
		{
			Name: "test-bad-part",
			WorkerFunc: func(version *eregs.Part) {
				version.Processed = true
			},
			Input: eregs.TitleConfig{
				Title: 43,
				Subchapters: eregs.SubchapterList{
					eregs.SubchapterArg{"IV", "C"},
				},
				Parts: eregs.PartList{"1", "2", "3"},
			},
			Error: true,
		},
	}

	for _, tc := range testTable {
		Run(t, tc.Name, func(t *testing.T) {
			WorkerFunc = tc.WorkerFunc
			err := parseTitle(&tc.Input)
			if err != nil && !tc.Error {
				t.Errorf("received unexpected error (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received none")
			}
		})
	}
}

func TestStartVersionWorker(t *testing.T) {
	SleepFunc = func(t time.Duration) {}

	input := [][]eregs.Part{
		[]eregs.Part{
			eregs.Part{
				Title: 42,
				Name:  "433",
				Date:  "2022-01-01",
			},
			eregs.Part{
				Title: 42,
				Name:  "433",
				Date:  "2022-02-01",
			},
		},
		[]eregs.Part{
			eregs.Part{
				Title: 42,
				Name:  "450",
				Date:  "2022-03-01",
			},
			eregs.Part{
				Title: 42,
				Name:  "433",
				Date:  "2022-04-01",
			},
		},
	}

	testTable := []struct {
		Name              string
		ShouldProcess     bool
		HandleVersionFunc func(context.Context, int, *eregs.Part) error
	}{
		{
			Name:          "test-valid-run",
			ShouldProcess: true,
			HandleVersionFunc: func(ctx context.Context, thread int, part *eregs.Part) error {
				return nil
			},
		},
		{
			Name:          "test-fail-run",
			ShouldProcess: false,
			HandleVersionFunc: func(ctx context.Context, thread int, part *eregs.Part) error {
				return fmt.Errorf("Oops something bad happened")
			},
		},
	}

	for _, tc := range testTable {
		Run(t, tc.Name, func(t *testing.T) {
			HandleVersionFunc = tc.HandleVersionFunc

			parts := list.New()
			for _, part := range input {
				versions := list.New()
				for _, version := range part {
					versions.PushBack(&version)
				}
				parts.PushBack(versions)
			}

			ch := make(chan *list.List)
			ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
			defer cancel()

			var wg sync.WaitGroup
			wg.Add(1)
			go startVersionWorker(ctx, 1, ch, &wg)
			for versionList := parts.Front(); versionList != nil; versionList = versionList.Next() {
				ch <- versionList.Value.(*list.List)
			}
			close(ch)
			wg.Wait()

			for part := parts.Front(); part != nil; part = part.Next() {
				for versionElement := part.Value.(*list.List).Front(); versionElement != nil; versionElement = versionElement.Next() {
					version := versionElement.Value.(*eregs.Part)
					if version.Processed != tc.ShouldProcess {
						t.Errorf("version.Processed: expected (%t), received (%t)", tc.ShouldProcess, version.Processed)
					}
				}
			}
		})
	}
}

func TestHandleVersion(t *testing.T) {
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
							"children": []
						}
					]
				}`))
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
		if r.Method != "PUT" {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "Expected PUT method, got ` + r.Method + `" }`))
			return
		}

		path := strings.Split(r.URL.Path, "/")
		if len(path) < 2 {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "Invalid PUT path '` + r.URL.Path + `'" }`))
		} else if path[1] == "part" {
			//posting a part
			d := json.NewDecoder(r.Body)
			var part struct{}
			if err := d.Decode(&part); err != nil {
				w.WriteHeader(http.StatusInternalServerError)
				errString := fmt.Sprintf("%+v", err)
				w.Write([]byte(`{ "exception": "PUT part - failed to parse JSON: '` + errString + `'" }`))
				return
			}
		} else {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "Invalid PUT path '` + r.URL.Path + `'" }`))
		}

		w.WriteHeader(http.StatusOK)
		w.Write([]byte("OK"))
	}))
	defer eregsServer.Close()
	eregs.BaseURL = eregsServer.URL

	testTable := []struct {
		Name     string
		Input    eregs.Part
		Expected eregs.Part
		Error    bool
	}{
		{
			Name: "test-valid",
			Input: eregs.Part{
				Title:           42,
				Name:            "433",
				Date:            "2022-01-01",
				Structure:       &ecfr.Structure{},
				Document:        &parsexml.Part{},
				UploadLocations: true,
			},
			Expected: eregs.Part{
				Title: 42,
				Name:  "433",
				Date:  "2022-01-01",
				Structure: &ecfr.Structure{
					Identifier:       ecfr.IdentifierString{"42"},
					Label:            "Title 42 - Public Health",
					LabelLevel:       "Title 42",
					LabelDescription: "Public Health",
					Reserved:         false,
					Type:             "title",
					Children: []*ecfr.Structure{
						&ecfr.Structure{
							Identifier:       ecfr.IdentifierString{"IV"},
							Label:            " Chapter IV - Centers for Medicare & Medicaid Services, Department of Health and Human Services",
							LabelLevel:       " Chapter IV",
							LabelDescription: "Centers for Medicare &amp; Medicaid Services, Department of Health and Human Services",
							Reserved:         false,
							Type:             "chapter",
							Children: []*ecfr.Structure{
								&ecfr.Structure{
									Identifier:       ecfr.IdentifierString{"C"},
									Label:            "Subchapter C - Medical Assistance Programs",
									LabelLevel:       "Subchapter C",
									LabelDescription: "Medical Assistance Programs",
									Reserved:         false,
									Type:             "subchapter",
									Children: []*ecfr.Structure{
										&ecfr.Structure{
											Identifier:       ecfr.IdentifierString{"433"},
											Label:            "Part 433 - State Fiscal Administration",
											LabelLevel:       "Part 433",
											LabelDescription: "State Fiscal Administration",
											Reserved:         false,
											Type:             "part",
											Children: []*ecfr.Structure{
												&ecfr.Structure{
													Identifier:       ecfr.IdentifierString{"433", "1"},
													Label:            "§ 433.1 Purpose.",
													LabelLevel:       "§ 433.1",
													LabelDescription: "Purpose.",
													Reserved:         false,
													Type:             "section",
													Children:         nil,
													DescendantRange:  nil,
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
					XMLName: xml.Name{
						Space: "",
						Local: "DIV5",
					},
					Structure: nil,
					Citation:  parsexml.SectionCitation{"433"},
					Type:      "PART",
					Header:    "PART 433 - STATE FISCAL ADMINISTRATION ",
					Authority: parsexml.Authority{
						Header:  "Authority:",
						Content: "42 U.S.C. 1302. ",
					},
					Source: parsexml.Source{
						Header:  "Source:",
						Content: "43 FR 45201, Sept. 29, 1978, unless otherwise noted. ",
					},
					Children: parsexml.PartChildren{
						&parsexml.Section{
							Type:     "SECTION",
							Citation: parsexml.SectionCitation{"433", "1"},
							Header:   "§ 433.1 Purpose.",
							Children: parsexml.SectionChildren{
								&parsexml.Paragraph{
									Type:     "Paragraph",
									Content:  "This part specifies the rates of FFP for services and administration, and prescribes requirements, prohibitions, and FFP conditions relating to State fiscal activities. ",
									Citation: parsexml.SectionCitation{"433", "1", "d78835ad878d59bddbcde2a31249107c"},
									Marker:   nil,
								},
							},
						},
					},
				},
			},
			Error: false,
		},
		{
			Name: "test-bad-fetch-structure",
			Input: eregs.Part{
				Title:     43,
				Name:      "433",
				Date:      "2022-01-01",
				Structure: &ecfr.Structure{},
				Document:  &parsexml.Part{},
			},
			Expected: eregs.Part{},
			Error:    true,
		},
		{
			Name: "test-unrecognized-path",
			Input: eregs.Part{
				Title:     44,
				Name:      "433",
				Date:      "2022-01-01",
				Structure: &ecfr.Structure{},
				Document:  &parsexml.Part{},
			},
			Expected: eregs.Part{},
			Error:    true,
		},
	}

	for _, tc := range testTable {
		Run(t, tc.Name, func(t *testing.T) {
			ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
			defer cancel()
			err := handleVersion(ctx, 1, &tc.Input)
			diff := deep.Equal(tc.Input.Document, tc.Expected.Document)
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
		Name     string
		Array    []string
		String   string
		Expected bool
	}{
		{
			Name:     "test-in-array",
			Array:    []string{"aaa", "bbb", "ccc"},
			String:   "bbb",
			Expected: true,
		},
		{
			Name:     "test-last-element",
			Array:    []string{"aaa", "bbb", "ccc"},
			String:   "ccc",
			Expected: true,
		},
		{
			Name:     "test-not-in-array",
			Array:    []string{"aaa", "bbb", "ccc"},
			String:   "ddd",
			Expected: false,
		},
	}

	for _, tc := range testTable {
		Run(t, tc.Name, func(t *testing.T) {
			out := contains(tc.Array, tc.String)
			if out != tc.Expected {
				t.Errorf("expected (%t), received (%t)", tc.Expected, out)
			}
		})
	}
}
