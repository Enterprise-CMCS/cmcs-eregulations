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
		Parts: []*eregs.PartConfig{
			&eregs.PartConfig{
				Title:           42,
				Type:            "subchapter",
				Value:           "IV-C",
				UploadRegText:   true,
				UploadLocations: true,
				UploadFRDocs:    true,
			},
			&eregs.PartConfig{
				Title:           42,
				Type:            "part",
				Value:           "400",
				UploadRegText:   true,
				UploadLocations: true,
				UploadFRDocs:    true,
			},
			&eregs.PartConfig{
				Title:           42,
				Type:            "part",
				Value:           "457",
				UploadRegText:   true,
				UploadLocations: true,
				UploadFRDocs:    true,
			},
			&eregs.PartConfig{
				Title:           42,
				Type:            "part",
				Value:           "460",
				UploadRegText:   true,
				UploadLocations: true,
				UploadFRDocs:    true,
			},
			&eregs.PartConfig{
				Title:           43,
				Type:            "subchapter",
				Value:           "AB-C",
				UploadRegText:   true,
				UploadLocations: true,
				UploadFRDocs:    true,
			},
			&eregs.PartConfig{
				Title:           43,
				Type:            "part",
				Value:           "1",
				UploadRegText:   true,
				UploadLocations: true,
				UploadFRDocs:    true,
			},
			&eregs.PartConfig{
				Title:           43,
				Type:            "part",
				Value:           "2",
				UploadRegText:   true,
				UploadLocations: true,
				UploadFRDocs:    true,
			},
			&eregs.PartConfig{
				Title:           43,
				Type:            "part",
				Value:           "3",
				UploadRegText:   true,
				UploadLocations: true,
				UploadFRDocs:    true,
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
		ParseTitleFunc     func(int, []*eregs.PartConfig) error
		RetrieveConfigFunc func() (*eregs.ParserConfig, int, error)
		Error              bool
	}{
		{
			Name: "test-success",
			ParseTitleFunc: func(title int, rawParts []*eregs.PartConfig) error {
				return nil
			},
			Error: false,
		},
		{
			Name: "test-parse-title-failure",
			ParseTitleFunc: func(title int, rawParts []*eregs.PartConfig) error {
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
	PostParserResultFunc = func(ctx context.Context, result *eregs.ParserResult) (int, error) { return 200, nil }
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
		Name                 string
		WorkerFunc           func(*eregs.Part)
		Title                int
		RawParts             []*eregs.PartConfig
		GetExistingPartsFunc func(context.Context, int) (map[string][]string, int, error)
		ProcessPartsListFunc func(context.Context, int, []*eregs.PartConfig) ([]*eregs.PartConfig, error)
		ExtractVersionsFunc  func(context.Context, int) (map[string]map[string]struct{}, error)
		Error                bool
	}{
		{
			Name: "test-valid",
			WorkerFunc: func(version *eregs.Part) {
				if version.Title == 42 && version.Name == "400" && version.Date == "2021-01-01" {
					version.Processed = true
				}
			},
			Title: 42,
			RawParts: []*eregs.PartConfig{
				&eregs.PartConfig{
					Type:            "part",
					Title:           42,
					Value:           "400",
					UploadLocations: true,
					UploadRegText:   true,
					UploadFRDocs:    true,
				},
			},
			GetExistingPartsFunc: func(ctx context.Context, title int) (map[string][]string, int, error) {
				return make(map[string][]string), 200, nil
			},
			ProcessPartsListFunc: func(ctx context.Context, title int, parts []*eregs.PartConfig) ([]*eregs.PartConfig, error) {
				return parts, nil
			},
			ExtractVersionsFunc: func(ctx context.Context, title int) (map[string]map[string]struct{}, error) {
				return map[string]map[string]struct{}{
					"400": map[string]struct{}{
						"2021-01-01": struct{}{},
					},
				}, nil
			},
			Error: false,
		},
		{
			Name: "test-process-fail",
			WorkerFunc: func(version *eregs.Part) {
				version.Processed = false
			},
			Title: 42,
			RawParts: []*eregs.PartConfig{
				&eregs.PartConfig{
					Type:            "part",
					Title:           42,
					Value:           "400",
					UploadLocations: true,
					UploadRegText:   true,
					UploadFRDocs:    true,
				},
			},
			GetExistingPartsFunc: func(ctx context.Context, title int) (map[string][]string, int, error) {
				return make(map[string][]string), 200, nil
			},
			ProcessPartsListFunc: func(ctx context.Context, title int, parts []*eregs.PartConfig) ([]*eregs.PartConfig, error) {
				return parts, nil
			},
			ExtractVersionsFunc: func(ctx context.Context, title int) (map[string]map[string]struct{}, error) {
				return map[string]map[string]struct{}{
					"400": map[string]struct{}{
						"2021-01-01": struct{}{},
					},
				}, nil
			},
			Error: true,
		},
		{
			Name: "test-existing-parts-fail",
			WorkerFunc: func(version *eregs.Part) {
				if version.Title == 42 && version.Name == "400" && version.Date == "2021-01-01" {
					version.Processed = true
				}
			},
			Title: 42,
			RawParts: []*eregs.PartConfig{
				&eregs.PartConfig{
					Type:            "part",
					Title:           42,
					Value:           "400",
					UploadLocations: true,
					UploadRegText:   true,
					UploadFRDocs:    true,
				},
			},
			GetExistingPartsFunc: func(ctx context.Context, title int) (map[string][]string, int, error) {
				return nil, 404, fmt.Errorf("oops")
			},
			ProcessPartsListFunc: func(ctx context.Context, title int, parts []*eregs.PartConfig) ([]*eregs.PartConfig, error) {
				return parts, nil
			},
			ExtractVersionsFunc: func(ctx context.Context, title int) (map[string]map[string]struct{}, error) {
				return map[string]map[string]struct{}{
					"400": map[string]struct{}{
						"2021-01-01": struct{}{},
					},
				}, nil
			},
			Error: false,
		},
		{
			Name: "test-process-parts-list-fail",
			WorkerFunc: func(version *eregs.Part) {
				if version.Title == 42 && version.Name == "400" && version.Date == "2021-01-01" {
					version.Processed = true
				}
			},
			Title: 42,
			RawParts: []*eregs.PartConfig{
				&eregs.PartConfig{
					Type:            "part",
					Title:           42,
					Value:           "400",
					UploadLocations: true,
					UploadRegText:   true,
					UploadFRDocs:    true,
				},
			},
			GetExistingPartsFunc: func(ctx context.Context, title int) (map[string][]string, int, error) {
				return make(map[string][]string), 200, nil
			},
			ProcessPartsListFunc: func(ctx context.Context, title int, parts []*eregs.PartConfig) ([]*eregs.PartConfig, error) {
				return nil, fmt.Errorf("oops")
			},
			ExtractVersionsFunc: func(ctx context.Context, title int) (map[string]map[string]struct{}, error) {
				return map[string]map[string]struct{}{
					"400": map[string]struct{}{
						"2021-01-01": struct{}{},
					},
				}, nil
			},
			Error: true,
		},
		{
			Name: "test-extract-versions-fail",
			WorkerFunc: func(version *eregs.Part) {
				if version.Title == 42 && version.Name == "400" && version.Date == "2021-01-01" {
					version.Processed = true
				}
			},
			Title: 42,
			RawParts: []*eregs.PartConfig{
				&eregs.PartConfig{
					Type:            "part",
					Title:           42,
					Value:           "400",
					UploadLocations: true,
					UploadRegText:   true,
					UploadFRDocs:    true,
				},
			},
			GetExistingPartsFunc: func(ctx context.Context, title int) (map[string][]string, int, error) {
				return make(map[string][]string), 200, nil
			},
			ProcessPartsListFunc: func(ctx context.Context, title int, parts []*eregs.PartConfig) ([]*eregs.PartConfig, error) {
				return parts, nil
			},
			ExtractVersionsFunc: func(ctx context.Context, title int) (map[string]map[string]struct{}, error) {
				return nil, fmt.Errorf("oops")
			},
			Error: true,
		},
	}

	for _, tc := range testTable {
		Run(t, tc.Name, func(t *testing.T) {
			WorkerFunc = tc.WorkerFunc
			GetExistingPartsFunc = tc.GetExistingPartsFunc
			ProcessPartsListFunc = tc.ProcessPartsListFunc
			ExtractVersionsFunc = tc.ExtractVersionsFunc
			err := parseTitle(tc.Title, tc.RawParts)
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
				UploadRegText:   true,
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
