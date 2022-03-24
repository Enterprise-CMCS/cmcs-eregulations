package eregs

import (
	"testing"
	"net/http/httptest"
	"net/http"
	"context"
	"time"
	"fmt"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"

	"github.com/go-test/deep"
)

func TestPostPart(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/" {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte("OK"))
		} else {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "Bad URL ` + r.URL.Path + `!" }`))
		}
	}))
	defer server.Close()
	BaseURL = server.URL

	ctx, cancel := context.WithTimeout(context.Background(), 1 * time.Second)
	defer cancel()

	part := &Part{
		Title: 1,
		Name: "test",
		Date: "2022-01-01",
		Structure: nil,
		Document: nil,
	}

	code, err := PostPart(ctx, part)

	if err != nil {
		t.Errorf("received error (%+v)", err)
	}

	if code != http.StatusOK {
		t.Errorf("received code (%d)", code)
	}
}

func TestPostSupplementalPart(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/supplemental_content" {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte("OK"))
		} else {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "Bad URL ` + r.URL.Path + `!" }`))
		}
	}))
	defer server.Close()
	BaseURL = server.URL

	ctx, cancel := context.WithTimeout(context.Background(), 1 * time.Second)
	defer cancel()

	part := ecfr.Part{
		Name: "test",
		Title: "1",
		Sections: []ecfr.Section{
			ecfr.Section{
				Title: "1",
				Part: "2",
				Section: "3",
			},
		},
	}

	code, err := PostSupplementalPart(ctx, part)

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
					"partName": [
						"431",
						"457"
					]
				},
				{
					"date": "2021-08-13",
					"partName": [
						"455"
					]
				},
				{
					"date": "2019-08-02",
					"partName": [
						"460"
					]
				},
				{
					"date": "2020-12-31",
					"partName": [
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

	ctx, cancel := context.WithTimeout(context.Background(), 1 * time.Second)
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

func TestGetTitle(t *testing.T) {
	testTable := []struct{
		Name string
		Title int
		Error bool
		ExpectedCode int
	}{
		{
			Name: "test-valid-title",
			Title: 42,
			Error: false,
			ExpectedCode: http.StatusOK,
		},
		{
			Name: "test-404",
			Title: 43,
			Error: true,
			ExpectedCode: http.StatusNotFound,
		},
		{
			Name: "test-server-error",
			Title: 44,
			Error: true,
			ExpectedCode: http.StatusInternalServerError,
		},
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/title/42" {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte(`{ "id": 1, "name": "42", "last_updated": "ABC", "toc": {} }`))
		} else if r.URL.Path == "/title/43" {
			w.WriteHeader(http.StatusNotFound)
			w.Write([]byte("NOT FOUND"))
		} else if r.URL.Path == "/title/44" {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte("BAD RESPONSE"))
		} else {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte("BAD PATH"))
		}
	}))
	defer server.Close()
	BaseURL = server.URL

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			ctx, cancel := context.WithTimeout(context.Background(), 1 * time.Second)
			defer cancel()
			_, code, err := GetTitle(ctx, tc.Title)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received none")
			}

			if code != tc.ExpectedCode {
				t.Errorf("expected code (%d), got (%d)", tc.ExpectedCode, code)
			}
		})
	}
}

func TestSendTitle(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/title/42" {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte("OK"))
		} else {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte("BAD PATH"))
		}
	}))
	defer server.Close()
	BaseURL = server.URL

	title := Title{
		Name: "42",
		Contents: &ecfr.Structure{},
		Exists: false,
		Modified: true,
	}
	
	ctx, cancel := context.WithTimeout(context.Background(), 1 * time.Second)
	defer cancel()

	code, err := SendTitle(ctx, &title)

	if err != nil {
		t.Errorf("received error (%+v)", err)
	}

	if code != http.StatusOK {
		t.Errorf("received code (%d)", code)
	}
}
