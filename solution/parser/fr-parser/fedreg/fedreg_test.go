package fedreg

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strconv"
	"testing"
	"time"

	"github.com/go-test/deep"
)

func TestFetchContent(t *testing.T) {
	testTable := []struct {
		Name   string
		Pages  [][]byte
		Output []*FRDoc
		Error  bool
	}{
		{
			Name: "test-single-page",
			Pages: [][]byte{
				[]byte(`{
					"results": [
						{
							"citation": "a citation",
							"title": "a title",
							"type": "a type",
							"html_url": "https://test.gov/test",
							"publication_date": "2021-01-31",
							"docket_ids": [
								"CMS-0000-F2",
								"CMS-0001-C1"
							],
							"document_number": "2021-12345"
						},
						{
							"citation": "a citation 2",
							"title": "a title 2",
							"type": "a type 2",
							"html_url": "https://test.gov/test/2",
							"publication_date": "2021-02-01",
							"docket_ids": [
								"CMS-0000-F3"
							],
							"document_number": "2021-67890"
						}
					]
				}`),
			},
			Output: []*FRDoc{
				&FRDoc{
					Name:        "a citation",
					Description: "a title",
					Category:    "a type",
					URL:         "https://test.gov/test",
					Date:        "2021-01-31",
					DocketNumbers: []string{
						"CMS-0000-F2",
						"CMS-0001-C1",
					},
					DocumentNumber: "2021-12345",
				},
				&FRDoc{
					Name:           "a citation 2",
					Description:    "a title 2",
					Category:       "a type 2",
					URL:            "https://test.gov/test/2",
					Date:           "2021-02-01",
					DocketNumbers:  []string{"CMS-0000-F3"},
					DocumentNumber: "2021-67890",
				},
			},
			Error: false,
		},
		{
			Name: "test-two-pages",
			Pages: [][]byte{
				[]byte(`{
					"next_page_url": "%s?page=2",
					"results": [
						{
							"citation": "a citation",
							"title": "a title",
							"type": "a type",
							"html_url": "https://test.gov/test",
							"publication_date": "2021-01-31",
							"docket_ids": [
								"CMS-0000-F2",
								"CMS-0001-C1"
							],
							"document_number": "2021-12345"
						},
						{
							"citation": "a citation 2",
							"title": "a title 2",
							"type": "a type 2",
							"html_url": "https://test.gov/test/2",
							"publication_date": "2021-02-01",
							"docket_ids": [
								"CMS-0000-F3"
							],
							"document_number": "2021-67890"
						}
					]
				}`),
				[]byte(`{
					"results": [
						{
							"citation": "a citation 3",
							"title": "a title 3",
							"type": "a type 3",
							"html_url": "https://test.gov/test/3",
							"publication_date": "2021-02-02",
							"docket_ids": [
								"CMS-0000-F4"
							],
							"document_number": "2021-09876"
						},
						{
							"citation": "a citation 4",
							"title": "a title 4",
							"type": "a type 4",
							"html_url": "https://test.gov/test/4",
							"publication_date": "2021-02-03",
							"docket_ids": [
								"CMS-0000-F5"
							],
							"document_number": "2021-54321"
						}
					]
				}`),
			},
			Output: []*FRDoc{
				&FRDoc{
					Name:        "a citation",
					Description: "a title",
					Category:    "a type",
					URL:         "https://test.gov/test",
					Date:        "2021-01-31",
					DocketNumbers: []string{
						"CMS-0000-F2",
						"CMS-0001-C1",
					},
					DocumentNumber: "2021-12345",
				},
				&FRDoc{
					Name:           "a citation 2",
					Description:    "a title 2",
					Category:       "a type 2",
					URL:            "https://test.gov/test/2",
					Date:           "2021-02-01",
					DocketNumbers:  []string{"CMS-0000-F3"},
					DocumentNumber: "2021-67890",
				},
				&FRDoc{
					Name:           "a citation 3",
					Description:    "a title 3",
					Category:       "a type 3",
					URL:            "https://test.gov/test/3",
					Date:           "2021-02-02",
					DocketNumbers:  []string{"CMS-0000-F4"},
					DocumentNumber: "2021-09876",
				},
				&FRDoc{
					Name:           "a citation 4",
					Description:    "a title 4",
					Category:       "a type 4",
					URL:            "https://test.gov/test/4",
					Date:           "2021-02-03",
					DocketNumbers:  []string{"CMS-0000-F5"},
					DocumentNumber: "2021-54321",
				},
			},
			Error: false,
		},
		{
			Name: "test-missing-page",
			Pages: [][]byte{
				[]byte(`{
					"next_page_url": "%s?page=2",
					"results": [
						{
							"citation": "a citation",
							"title": "a title",
							"type": "a type",
							"html_url": "https://test.gov/test",
							"publication_date": "2021-01-31",
							"docket_ids": [
								"CMS-0000-F2",
								"CMS-0001-C1"
							],
							"document_number": "2021-12345"
						},
						{
							"citation": "a citation 2",
							"title": "a title 2",
							"type": "a type 2",
							"html_url": "https://test.gov/test/2",
							"publication_date": "2021-02-01",
							"docket_ids": [
								"CMS-0000-F3"
							],
							"document_number": "2021-67890"
						}
					]
				}`),
				[]byte(`{
					"next_page_url": "%s?page=3",
					"results": [
						{
							"citation": "a citation 3",
							"title": "a title 3",
							"type": "a type 3",
							"html_url": "https://test.gov/test/3",
							"publication_date": "2021-02-02",
							"docket_ids": [
								"CMS-0000-F4"
							],
							"document_number": "2021-09876"
						},
						{
							"citation": "a citation 4",
							"title": "a title 4",
							"type": "a type 4",
							"html_url": "https://test.gov/test/4",
							"publication_date": "2021-02-03",
							"docket_ids": [
								"CMS-0000-F5"
							],
							"document_number": "2021-54321"
						}
					]
				}`),
			},
			Output: nil,
			Error:  true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				keys, ok := r.URL.Query()["page"]
				if !ok || len(keys[0]) < 1 {
					if len(tc.Pages) > 0 {
						w.WriteHeader(http.StatusOK)
						w.Write(tc.Pages[0])
						return
					}
				}
				page, err := strconv.Atoi(keys[0])
				if err == nil && len(tc.Pages) >= page {
					w.WriteHeader(http.StatusOK)
					w.Write(tc.Pages[page-1])
					return
				}
				w.WriteHeader(http.StatusNotFound)
				w.Write([]byte(`{ "exception": "URL not valid!" }`))
			}))
			defer server.Close()
			FedRegContentURL = server.URL + "/%d/%s"
			for i, page := range tc.Pages {
				tc.Pages[i] = []byte(fmt.Sprintf(string(page), server.URL))
			}

			ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
			defer cancel()

			output, err := FetchContent(ctx, 42, "433")
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received (%+v)", output)
			} else if diff := deep.Equal(output, tc.Output); diff != nil {
				t.Errorf("output not as expected: (%+v)", diff)
			}
		})
	}
}

func TestFetchSections(t *testing.T) {
	testTable := []struct {
		Name     string
		InputXML []byte
		Sections   []string
		PartMap map[string]string
		Error    bool
	}{
		{
			Name: "test-valid-sections",
			InputXML: []byte(`
				<PRORULE>
					<PREAMB>
						<SUBAGY>Centers for Medicare &amp; Medicaid Services</SUBAGY>
						<CFR>42 CFR Parts 438, 440, 457, and 460</CFR>
					</PREAMB>
					<TEST>Some data</TEST>
					<SUPLINF>
						<SECTION>
							<SECTNO>§ 447.502 </SECTNO>
							<SUBJECT>Definitions.</SUBJECT>
							<STARS/>
						</SECTION>
						<SECTION>
							<SECTNO>§ 33.118 </SECTNO>
							<SUBJECT>abc xyz...</SUBJECT>
							<STARS/>
						</SECTION>
					</SUPLINF>
				</PRORULE>
			`),
			Sections: []string{"447.502", "33.118"},
			PartMap: map[string]string{
				"438": "42",
				"440": "42",
				"457": "42",
				"460": "42",
			},
			Error:  false,
		},
		{
			Name: "test-bad-xml",
			InputXML: []byte(`
				PRORULE>
					<TEST>Some data</TEST>
					<SUPLINF>
						<SECTION>
							<SECTNO>§ 447.502 </SECTNO>
							<SUBJECT>Definitions.</SUBJECT>
							<STARS/>
						</SECTION>
						<SECTION>
							<SECTNO>§ 33.118 </SECTNO>
							<SUBJECT>abc xyz...</SUBJECT>
							<STARS/>
						</SECTION>
					</SUPLINF>
				</PRORULE>
			`),
			Sections: nil,
			PartMap: nil,
			Error:  true,
		},
		{
			Name: "test-bad-sectno",
			InputXML: []byte(`
				<PRORULE>
					<TEST>Some data</TEST>
					<SUPLINF>
						<SECTION>
							<SECTNO>§ 447.502 </SECTNO>
							<SUBJECT>Definitions.</SUBJECT>
							<STARS/>
						</SECTION>
						<SECTION>
							<SECTNO><ABC></SECTNO>
							<SUBJECT>abc xyz...</SUBJECT>
							<STARS/>
						</SECTION>
					</SUPLINF>
				</PRORULE>
			`),
			Sections: nil,
			PartMap: nil,
			Error:  true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusOK)
				w.Write(tc.InputXML)
			}))
			defer server.Close()

			ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
			defer cancel()

			sections, partMap, err := FetchSections(ctx, server.URL)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received sections (%+v), part map (%+v)", sections, partMap)
			} else {
				if diff := deep.Equal(sections, tc.Sections); diff != nil {
					t.Errorf("sections not as expected: (%+v)", diff)
				}
				if diff := deep.Equal(partMap, tc.PartMap); diff != nil {
					t.Errorf("part map not as expected: (%+v)", diff)
				}
			}
		})
	}
}

func TestExtractSection(t *testing.T) {
	testTable := []struct {
		Name   string
		Input  string
		Output string
		Error  bool
	}{
		{
			Name:   "test-valid",
			Input:  "§ 430.12",
			Output: "430.12",
			Error:  false,
		},
		{
			Name:   "test-invisible-space",
			Input:  "§ㅤ430.11",
			Output: "430.11",
			Error:  false,
		},
		{
			Name:   "test-invalid",
			Input:  "§ 430",
			Output: "",
			Error:  true,
		},
		{
			Name:   "test-no-symbol",
			Input:  "430.10",
			Output: "430.10",
			Error:  false,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			output, err := extractSection(tc.Input)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received (%s)", output)
			} else if diff := deep.Equal(output, tc.Output); diff != nil {
				t.Errorf("output not as expected: (%+v)", diff)
			}
		})
	}
}

func TestExtractCFR(t *testing.T) {
	testTable := []struct {
		Name   string
		Input  string
		Title string
		Parts []string
		Error  bool
	}{
		{
			Name:   "test-multi-part",
			Input:  "45 CFR Parts 80, 84, 86, 91, 92, 147, 155, and 156",
			Title: "45",
			Parts: []string{"80", "84", "86", "91", "92", "147", "155", "156"},
			Error:  false,
		},
		{
			Name:   "test-single-part",
			Input:  "42 CFR Part 438.",
			Title: "42",
			Parts: []string{"438"},
			Error:  false,
		},
		{
			Name:   "test-no-parts",
			Input:  "42 CFR Part",
			Title: "",
			Parts: nil,
			Error:  true,
		},
		{
			Name:   "test-empty-string",
			Input:  "   ",
			Title: "",
			Parts: nil,
			Error:  true,
		},
		{
			Name:   "test-invalid-title",
			Input:  "blah CFR Part 438.",
			Title: "",
			Parts: nil,
			Error:  true,
		},
		{
			Name:   "test-title-only",
			Input:  "42",
			Title: "",
			Parts: nil,
			Error:  true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			title, parts, err := extractCFR(tc.Input)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received title (%s) parts (%+v)", title, parts)
			} else if title != tc.Title {
				t.Errorf("expected title (%s), received title (%s)", tc.Title, title)
			} else if diff := deep.Equal(parts, tc.Parts); diff != nil {
				t.Errorf("output not as expected: (%+v)", diff)
			}
		})
	}
}
