package ecfr

import (
	"testing"
	"net/http/httptest"
	"net/http"
	"net/url"
	"context"
	"fmt"
	"time"

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
	}{
		{
			Name: "",
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {

		})
	}
}

func TestSubchapterOptionValues(t *testing.T) {
	testTable := []struct {
		Name string
	}{
		{
			Name: "",
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {

		})
	}
}
