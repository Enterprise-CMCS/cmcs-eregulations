package ecfr

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"net/url"
	"testing"
	"time"

	"github.com/cmsgov/cmcs-eregulations/lib/network"
	"github.com/go-test/deep"
)

type TestOption struct {
	Name  string
	Value string
}

func (t *TestOption) Values() url.Values {
	v := url.Values{}
	v.Set(t.Name, t.Value)
	return v
}

func TestFetchFunctions(t *testing.T) {
	var path string

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != path {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "Bad URL ` + r.URL.Path + `" }`))
			return
		}

		query := r.URL.Query()
		keys, ok := query["hello"]
		if !ok || len(keys[0]) < 1 || string(keys[0]) != "world" {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "'hello' key or 'world' value missing" }`))
			return
		}
		keys, ok = query["asdf"]
		if !ok || len(keys[0]) < 1 || string(keys[0]) != "fdsa" {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{ "exception": "'asdf' key or 'fdsa' value missing" }`))
			return
		}

		w.WriteHeader(http.StatusOK)
		w.Write([]byte("OK"))
	}))
	defer server.Close()
	EcfrSite = server.URL

	testTable := []struct {
		Name     string
		Path     string
		Function func(context.Context, ...network.FetchOption) (int, error)
	}{
		{
			Name: "test-fetch-full",
			Path: "/" + fmt.Sprintf(ecfrFullXML, "2022-01-01", 42),
			Function: func(ctx context.Context, opts ...network.FetchOption) (int, error) {
				_, code, err := FetchFull(ctx, "2022-01-01", 42, opts...)
				return code, err
			},
		},
		{
			Name: "test-fetch-structure",
			Path: "/" + fmt.Sprintf(ecfrStructureJSON, 42),
			Function: func(ctx context.Context, opts ...network.FetchOption) (int, error) {
				_, code, err := FetchStructure(ctx, 42, opts...)
				return code, err
			},
		},
		{
			Name: "test-fetch-versions",
			Path: "/" + fmt.Sprintf(ecfrVersionsXML, 42),
			Function: func(ctx context.Context, opts ...network.FetchOption) (int, error) {
				_, code, err := FetchVersions(ctx, 42, opts...)
				return code, err
			},
		},
	}

	opt1 := TestOption{"hello", "world"}
	opt2 := TestOption{"asdf", "fdsa"}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
			defer cancel()
			path = tc.Path
			code, err := tc.Function(ctx, &opt1, &opt2)
			if err != nil {
				t.Errorf("received error (%+v)", err)
			}
			if code != http.StatusOK {
				t.Errorf("received code (%d)", code)
			}
		})
	}
}

func TestPartOptionValues(t *testing.T) {
	testTable := []struct {
		Name   string
		Input  PartOption
		Output url.Values
	}{
		{
			Name:  "test-valid-partoption",
			Input: PartOption{"100"},
			Output: url.Values{
				"part": []string{"100"},
			},
		},
		{
			Name:  "test-empty-partoption",
			Input: PartOption{},
			Output: url.Values{
				"part": []string{""},
			},
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			output := tc.Input.Values()
			if diff := deep.Equal(output, tc.Output); diff != nil {
				t.Errorf("output not as expected: %+v", diff)
			}
		})
	}
}

func TestSubchapterOptionValues(t *testing.T) {
	testTable := []struct {
		Name   string
		Input  SubchapterOption
		Output url.Values
	}{
		{
			Name: "test-valid-subchapteroption",
			Input: SubchapterOption{
				Chapter:    "IV",
				Subchapter: "C",
			},
			Output: url.Values{
				"chapter":    []string{"IV"},
				"subchapter": []string{"C"},
			},
		},
		{
			Name:  "test-empty-subchapteroption",
			Input: SubchapterOption{},
			Output: url.Values{
				"chapter":    []string{""},
				"subchapter": []string{""},
			},
		},
		{
			Name: "test-single-value-subchapteroption",
			Input: SubchapterOption{
				Chapter: "ABC",
			},
			Output: url.Values{
				"chapter":    []string{"ABC"},
				"subchapter": []string{""},
			},
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			output := tc.Input.Values()
			if diff := deep.Equal(output, tc.Output); diff != nil {
				t.Errorf("output not as expected: %+v", diff)
			}
		})
	}
}
