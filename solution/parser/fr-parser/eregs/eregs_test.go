package eregs

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/go-test/deep"
)

func TestSendDocument(t *testing.T) {
	testTable := []struct {
		Name   string
		Server *httptest.Server
		Input  FRDoc
		Error  bool
	}{
		{
			Name: "test-valid",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				var fr FRDoc
				d := json.NewDecoder(r.Body)
				err := d.Decode(&fr)
				if err != nil {
					w.WriteHeader(http.StatusBadRequest)
					w.Write([]byte(`{ "exception": "` + err.Error() + `" }`))
				} else {
					w.WriteHeader(http.StatusOK)
					w.Write([]byte(`OK`))
				}
			})),
			Input: FRDoc{
				Name:        "this is a name",
				Description: "this is a description",
				DocType:     "this is a doc type",
				URL:         "https://test.gov/test",
				Date:        "2021-01-31",
				DocketNumbers: []string{
					"CMS-0000-F2",
					"CMS-0001-C1",
				},
				DocumentNumber: "2021-12345",
				Locations: []*Section{
					&Section{
						Title:   "42",
						Part:    "433",
						Section: "1",
					},
					&Section{
						Title:   "45",
						Part:    "450",
						Section: "10",
					},
				},
			},
			Error: false,
		},
		{
			Name: "test-server-error",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusInternalServerError)
				w.Write([]byte(`{ "exception": "This is expected" }`))
			})),
			Input: FRDoc{},
			Error: true,
		},
		{
			Name:   "test-no-connection",
			Server: nil,
			Input:  FRDoc{},
			Error:  true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			if tc.Server != nil {
				defer tc.Server.Close()
				BaseURL = tc.Server.URL
			} else {
				server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					w.WriteHeader(http.StatusInternalServerError)
					w.Write([]byte(`{ "exception": "This should never be seen" }`))
				}))
				BaseURL = server.URL
				server.Close()
			}

			ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
			defer cancel()

			err := SendDocument(ctx, &tc.Input)

			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received none")
			}
		})
	}
}

func TestCreateSections(t *testing.T) {
	sections := []string{
		"443.42",
		"1.1",
		"443.",
		".42",
		".",
		"",
		"123.45",
	}

	partMap := map[string]string{
		"443": "42",
		"123": "45",
	}

	expected := []*Section{
		&Section{
			Title:   "42",
			Part:    "443",
			Section: "42",
		},
		&Section{
			Title:   "45",
			Part:    "123",
			Section: "45",
		},
	}

	output := CreateSections(sections, partMap)
	if diff := deep.Equal(expected, output); diff != nil {
		t.Errorf("output not as expected: %+v", diff)
	}
}

func TestFetchDocumentList(t *testing.T) {
	testTable := []struct {
		Name     string
		Server   *httptest.Server
		Expected []string
		Error    bool
	}{
		{
			Name: "test-success",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusOK)
				w.Write([]byte(`[
					"https://test.gov/test",
					"https://test.gov/test2"
				]`))
			})),
			Expected: []string{
				"https://test.gov/test",
				"https://test.gov/test2",
			},
			Error: false,
		},
		{
			Name:     "test-server-error",
			Server:   nil,
			Expected: nil,
			Error:    true,
		},
		{
			Name: "test-server-error",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusInternalServerError)
				w.Write([]byte(`{ "exception": "this is expected" }`))
			})),
			Expected: nil,
			Error:    true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			if tc.Server == nil {
				tempServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					w.WriteHeader(http.StatusInternalServerError)
					w.Write([]byte(`{ "exception": "this should never appear" }`))
				}))
				BaseURL = tempServer.URL
				tempServer.Close()
			} else {
				BaseURL = tc.Server.URL
				defer tc.Server.Close()
			}

			ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
			defer cancel()

			output, err := FetchDocumentList(ctx)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received (%+v)", output)
			} else if diff := deep.Equal(output, tc.Expected); diff != nil {
				t.Errorf("output not as expected: (%+v)", diff)
			}
		})
	}
}
