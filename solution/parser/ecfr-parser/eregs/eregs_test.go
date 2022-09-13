package eregs

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"

	"github.com/go-test/deep"
)

func TestPostPart(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/part" {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte("OK"))
		} else {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "Bad URL ` + r.URL.Path + `!" }`))
		}
	}))
	defer server.Close()
	BaseURL = server.URL

	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	part := &Part{
		Title:     1,
		Name:      "test",
		Date:      "2022-01-01",
		Structure: nil,
		Document:  nil,
		Sections: []ecfr.Section{
			ecfr.Section{
				Title: "42",
				Part: "433",
				Section: "1",
			},
		},
		Subparts: []ecfr.Subpart{
			ecfr.Subpart{
				Title: "42",
				Part: "433",
				Subpart: "A",
				Sections: []ecfr.Section{
					ecfr.Section{
						Title: "42",
						Part: "433",
						Section: "2",
					},
				},
			},
		},
	}

	code, err := PutPart(ctx, part)

	if err != nil {
		t.Errorf("received error (%+v)", err)
	}

	if code != http.StatusOK {
		t.Errorf("received code (%d)", code)
	}
}

func TestGetExistingParts(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != fmt.Sprintf(partURL, 42) {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "Bad URL ` + r.URL.Path + `!" }`))
		} else {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte(`[
				{
					"date": "2017-08-04",
					"part_name": [
						"431",
						"457"
					]
				},
				{
					"date": "2021-08-13",
					"part_name": [
						"455"
					]
				},
				{
					"date": "2019-08-02",
					"part_name": [
						"460"
					]
				},
				{
					"date": "2020-12-31",
					"part_name": [
						"438",
						"433",
						"447",
						"456"
					]
				}
			]`))
		}
	}))
	defer server.Close()
	BaseURL = server.URL

	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	results, code, err := GetExistingParts(ctx, 42)

	if err != nil {
		t.Errorf("received error (%+v)", err)
	}

	if code != http.StatusOK {
		t.Errorf("received code (%d)", code)
	}

	expected := map[string][]string{
		"2017-08-04": []string{"431", "457"},
		"2019-08-02": []string{"460"},
		"2020-12-31": []string{"438", "433", "447", "456"},
		"2021-08-13": []string{"455"},
	}

	if diff := deep.Equal(results, expected); diff != nil {
		t.Errorf("output not as expected: %+v", diff)
	}
}

func TestPostParserResult(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/ecfr_parser_result/42" {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte("OK"))
		} else {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte("BAD PATH"))
		}
	}))
	defer server.Close()
	BaseURL = server.URL

	result := ParserResult{
		Start:           time.Now().Format(time.RFC3339),
		Title:           42,
		Parts:           "1,2,3",
		Subchapters:     "A,B,C",
		Workers:         3,
		Errors:          0,
		TotalVersions:   100,
		SkippedVersions: 99,
	}

	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	code, err := PostParserResult(ctx, &result)

	if err != nil {
		t.Errorf("received error (%+v)", err)
	}

	if code != http.StatusOK {
		t.Errorf("received code (%d)", code)
	}
}
