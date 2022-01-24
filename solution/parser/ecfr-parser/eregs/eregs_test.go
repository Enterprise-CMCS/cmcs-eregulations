package eregs

import (
	"testing"
	"reflect"
	"net/http/httptest"
	"net/http"
	"context"
	"time"
	"fmt"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
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

	if err := PostPart(ctx, part); err != nil {
		t.Errorf("received error (%+v)", err)
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

	if err := PostSupplementalPart(ctx, part); err != nil {
		t.Errorf("received error (%+v)", err)
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

	results, err := GetExistingParts(ctx, 42)
	if err != nil {
		t.Errorf("received error (%+v)", err)
	}

	expected := map[string][]string{
		"2017-08-04": []string{"431", "457"},
		"2019-08-02": []string{"460"},
		"2020-12-31": []string{"438", "433", "447", "456"},
		"2021-08-13": []string{"455"},
	}

	if !reflect.DeepEqual(results, expected) {
		t.Errorf("expected (%+v), got (%+v)", expected, results)
	}
}
