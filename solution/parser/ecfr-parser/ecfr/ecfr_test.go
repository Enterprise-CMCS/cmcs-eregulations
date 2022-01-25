package ecfr

import (
	"testing"
	"net/http/httptest"
	"net/http"
	"net/url"
	"context"
	"fmt"
	"time"
	"reflect"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/network"
)

type TestOption struct {
	Name string
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
	ecfrSite = server.URL
	
	testTable := []struct {
		Name string
		Path string
		Function func(context.Context, ...network.FetchOption) error
	}{
		{
			Name: "test-fetch-full",
			Path: "/" + fmt.Sprintf(ecfrFullXML, "2022-01-01", 42),
			Function: func(ctx context.Context, opts ...network.FetchOption) error {
				_, err := FetchFull(ctx, "2022-01-01", 42, opts...)
				if err != nil {
					return err
				}
				return nil
			},
		},
		{
			Name: "test-fetch-structure",
			Path: "/" + fmt.Sprintf(ecfrStructureJSON, "2022-01-01", 42),
			Function: func(ctx context.Context, opts ...network.FetchOption) error {
				_, err := FetchStructure(ctx, "2022-01-01", 42, opts...)
				if err != nil {
					return err
				}
				return nil
			},
		},
		{
			Name: "test-fetch-versions",
			Path: "/" + fmt.Sprintf(ecfrVersionsXML, 42),
			Function: func(ctx context.Context, opts ...network.FetchOption) error {
				_, err := FetchVersions(ctx, 42, opts...)
				if err != nil {
					return err
				}
				return nil
			},
		},
	}

	opt1 := TestOption{"hello", "world"}
	opt2 := TestOption{"asdf", "fdsa"}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			ctx, cancel := context.WithTimeout(context.Background(), 1 * time.Second)
			defer cancel()
			path = tc.Path
			err := tc.Function(ctx, &opt1, &opt2)
			if err != nil {
				t.Errorf("received error (%+v)", err)
			}
		})
	}
}

func TestPartOptionValues(t *testing.T) {
	testTable := []struct {
		Name string
		Input PartOption
		Output url.Values
	}{
		{
			Name: "test-valid-partoption",
			Input: PartOption{"100"},
			Output: url.Values{
				"part": []string{"100"},
			},
		},
		{
			Name: "test-empty-partoption",
			Input: PartOption{},
			Output: url.Values{
				"part": []string{""},
			},
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			output := tc.Input.Values()
			if !reflect.DeepEqual(output, tc.Output) {
				t.Errorf("expected (%+v), received (%+v)", tc.Output, output)
			}
		})
	}
}

func TestSubchapterOptionValues(t *testing.T) {
	testTable := []struct {
		Name string
		Input SubchapterOption
		Output url.Values
	}{
		{
			Name: "test-valid-subchapteroption",
			Input: SubchapterOption{
				Chapter: "IV",
				Subchapter: "C",
			},
			Output: url.Values{
				"chapter": []string{"IV"},
				"subchapter": []string{"C"},				
			},
		},
		{
			Name: "test-empty-subchapteroption",
			Input: SubchapterOption{},
			Output: url.Values{
				"chapter": []string{""},
				"subchapter": []string{""},
			},
		},
		{
			Name: "test-single-value-subchapteroption",
			Input: SubchapterOption{
				Chapter: "ABC",
			},
			Output: url.Values{
				"chapter": []string{"ABC"},
				"subchapter": []string{""},
			},
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			output := tc.Input.Values()
			if !reflect.DeepEqual(output, tc.Output) {
				t.Errorf("expected (%+v), received (%+v)", tc.Output, output)
			}
		})
	}
}
