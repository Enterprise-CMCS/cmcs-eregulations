package ecfr

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/go-test/deep"
)

func TestPartVersions(t *testing.T) {
	input := []Version{
		Version{
			Date: "2016-01-01",
			Part: "10",
		},
		Version{
			Date: "2018-01-01",
			Part: "10",
		},
		Version{
			Date: "2019-01-01",
			Part: "10",
		},
		Version{
			Date: "2020-01-01",
			Part: "12",
		},
		Version{
			Date: "2021-01-01",
			Part: "12",
		},
		Version{
			Date: "2022-01-01",
			Part: "10",
		},
	}

	expected := map[string]map[string]struct{}{
		"10": map[string]struct{}{
			"2017-01-01": struct{}{},
			"2018-01-01": struct{}{},
			"2019-01-01": struct{}{},
			"2022-01-01": struct{}{},
		},
		"12": map[string]struct{}{
			"2020-01-01": struct{}{},
			"2021-01-01": struct{}{},
		},
	}

	output := PartVersions(input)

	if diff := deep.Equal(output, expected); diff != nil {
		t.Errorf("output not as expected: %+v", diff)
	}
}

func TestExtractVersions(t *testing.T) {
	testTable := []struct {
		Name     string
		Server   *httptest.Server
		Expected map[string]map[string]struct{}
		Error    bool
	}{
		{
			Name: "test-valid-response",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusOK)
				w.Write([]byte(`{
					"content_versions": [
						{
							"date": "2016-12-19",
							"identifier": "10.1",
							"name": "§ 10.1   Purpose.",
							"part": "10",
							"removed": false,
							"subpart": "A",
							"title": "42",
							"type": "section"
						},
						{
							"date": "2018-12-19",
							"identifier": "10.10",
							"name": "§ 10.10   Entities eligible to participate in the 340B Drug Pricing Program.",
							"part": "10",
							"removed": false,
							"subpart": "B",
							"title": "42",
							"type": "section"
						},
						{
							"date": "2018-12-19",
							"identifier": "10.2",
							"name": "§ 10.2   Summary of 340B Drug Pricing Program.",
							"part": "10",
							"removed": false,
							"subpart": "A",
							"title": "42",
							"type": "section"
						},
						{
							"date": "2016-01-18",
							"identifier": "11.10",
							"name": "§ 11.10   What definitions apply to this part?",
							"part": "11",
							"removed": false,
							"subpart": "A",
							"title": "42",
							"type": "section"
						},
						{
							"date": "2018-01-18",
							"identifier": "11.2",
							"name": "§ 11.2   What is the purpose of this part?",
							"part": "11",
							"removed": false,
							"subpart": "A",
							"title": "42",
							"type": "section"
						},
						{
							"date": "2019-01-18",
							"identifier": "11.20",
							"name": "§ 11.20   Who must submit clinical trial registration information?",
							"part": "11",
							"removed": false,
							"subpart": "B",
							"title": "42",
							"type": "section"
						}
					]
				}`))
			})),
			Expected: map[string]map[string]struct{}{
				"10": map[string]struct{}{
					"2017-01-01": struct{}{},
					"2018-12-19": struct{}{},
				},
				"11": map[string]struct{}{
					"2017-01-01": struct{}{},
					"2018-01-18": struct{}{},
					"2019-01-18": struct{}{},
				},
			},
			Error: false,
		},
		{
			Name: "test-server-error",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusInternalServerError)
				w.Write([]byte(`{ "exception": "this is expected" }`))
			})),
			Expected: map[string]map[string]struct{}{},
			Error:    true,
		},
		{
			Name: "test-bad-json",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusOK)
				w.Write([]byte(`{ "exception" "this is bad JSON" `))
			})),
			Expected: map[string]map[string]struct{}{},
			Error:    true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			defer tc.Server.Close()
			EcfrSite = tc.Server.URL
			ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
			defer cancel()

			out, err := ExtractVersions(ctx, 42)

			diff := deep.Equal(out, tc.Expected)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received (%+v)", out)
			} else if err == nil && diff != nil {
				t.Errorf("output not as expected: %+v", diff)
			}
		})
	}
}

func TestExtractPartVersions(t *testing.T) {
	testTable := []struct {
		Name     string
		Server   *httptest.Server
		Expected map[string]struct{}
		Error    bool
	}{
		{
			Name: "test-valid-response",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusOK)
				w.Write([]byte(`{
					"content_versions": [
						{
							"date": "2016-12-19",
							"identifier": "10.1",
							"name": "§ 10.1   Purpose.",
							"part": "10",
							"removed": false,
							"subpart": "A",
							"title": "42",
							"type": "section"
						},
						{
							"date": "2018-12-19",
							"identifier": "10.10",
							"name": "§ 10.10   Entities eligible to participate in the 340B Drug Pricing Program.",
							"part": "10",
							"removed": false,
							"subpart": "B",
							"title": "42",
							"type": "section"
						},
						{
							"date": "2018-12-19",
							"identifier": "10.2",
							"name": "§ 10.2   Summary of 340B Drug Pricing Program.",
							"part": "10",
							"removed": false,
							"subpart": "A",
							"title": "42",
							"type": "section"
						},
						{
							"date": "2016-01-18",
							"identifier": "11.10",
							"name": "§ 11.10   What definitions apply to this part?",
							"part": "11",
							"removed": false,
							"subpart": "A",
							"title": "42",
							"type": "section"
						},
						{
							"date": "2018-01-18",
							"identifier": "11.2",
							"name": "§ 11.2   What is the purpose of this part?",
							"part": "11",
							"removed": false,
							"subpart": "A",
							"title": "42",
							"type": "section"
						},
						{
							"date": "2019-01-18",
							"identifier": "11.20",
							"name": "§ 11.20   Who must submit clinical trial registration information?",
							"part": "11",
							"removed": false,
							"subpart": "B",
							"title": "42",
							"type": "section"
						}
					]
				}`))
			})),
			Expected: map[string]struct{}{
				"2017-01-01": struct{}{},
				"2018-12-19": struct{}{},
			},
			Error: false,
		},
		{
			Name: "test-server-error",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusInternalServerError)
				w.Write([]byte(`{ "exception": "this is expected" }`))
			})),
			Expected: map[string]struct{}{},
			Error:    true,
		},
		{
			Name: "test-bad-json",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusOK)
				w.Write([]byte(`{ "exception" "this is bad JSON" `))
			})),
			Expected: map[string]struct{}{},
			Error:    true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			defer tc.Server.Close()
			EcfrSite = tc.Server.URL
			ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
			defer cancel()

			part := PartOption{
				Part: "10",
			}

			out, err := ExtractPartVersions(ctx, 42, &part)

			diff := deep.Equal(out, tc.Expected)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received (%+v)", out)
			} else if err == nil && diff != nil {
				t.Errorf("output not as expected: %+v", diff)
			}
		})
	}
}
