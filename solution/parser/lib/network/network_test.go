package network

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"net/url"
	"sort"
	"testing"
	"time"

	"github.com/go-test/deep"
)

func TestFetch(t *testing.T) {
	testTable := []struct {
		Name             string
		Server           *httptest.Server
		ExpectedResponse []byte
		ErrorExpected    bool
		ExpectedCode     int
		JSONErrors       bool
	}{
		{
			Name: "fetch-succeed-test",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusOK)
				w.Write([]byte("This is an arbitrary array of bytes"))
			})),
			ExpectedResponse: []byte("This is an arbitrary array of bytes"),
			ErrorExpected:    false,
			ExpectedCode:     http.StatusOK,
			JSONErrors:       false,
		},
		{
			Name: "fetch-fail-test",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusInternalServerError)
				w.Write([]byte(`{ "exception": "This request failed, as expected" }`))
			})),
			ExpectedResponse: nil,
			ErrorExpected:    true,
			ExpectedCode:     http.StatusInternalServerError,
			JSONErrors:       false,
		},
		{
			Name: "fetch-json-errors-test",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusOK)
				keys, ok := r.URL.Query()["json_errors"]
				if !ok || len(keys[0]) < 1 {
					w.Write([]byte("json_errors parameter NOT found!"))
				} else {
					w.Write([]byte("json_errors parameter found!"))
				}
			})),
			ExpectedResponse: []byte("json_errors parameter found!"),
			ErrorExpected:    false,
			ExpectedCode:     http.StatusOK,
			JSONErrors:       true,
		},
		{
			Name: "fetch-timeout-test",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				time.Sleep((1 * time.Second) + (500 * time.Millisecond))
				w.WriteHeader(http.StatusOK)
				w.Write([]byte("This request will cause a context timeout"))
			})),
			ExpectedResponse: nil,
			ErrorExpected:    true,
			ExpectedCode:     -1,
			JSONErrors:       false,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			defer tc.Server.Close()
			testURL, err := url.Parse(tc.Server.URL)
			if err != nil {
				t.Errorf("error parsing url '%s': %+v", tc.Server.URL, err)
			}
			ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
			defer cancel()

			body, code, err := Fetch(ctx, testURL, tc.JSONErrors, nil)

			if err == nil && tc.ErrorExpected {
				t.Errorf("expected error, got nil")
			} else if err != nil && !tc.ErrorExpected {
				t.Errorf("expected no error, got (%+v)", err)
			}

			if code != tc.ExpectedCode {
				t.Errorf("expected code (%d), got (%d)", tc.ExpectedCode, code)
			}

			if body != nil {
				response, err := io.ReadAll(body)
				if err != nil {
					t.Errorf("unable to extract bytes from response: %+v", err)
				}
				if diff := deep.Equal(response, tc.ExpectedResponse); diff != nil {
					t.Errorf("output not as expected: %+v", diff)
				}
			} else if tc.ExpectedResponse != nil {
				t.Errorf("expected (%s), got nil", tc.ExpectedResponse)
			}
		})
	}
}

type PostData struct {
	Name  string `json:"name"`
	ID    int    `json:"id"`
	Valid bool   `json:"yes"`
}

func TestSendJSON(t *testing.T) {
	testTable := []struct {
		Name          string
		Server        *httptest.Server
		PostData      *PostData
		ErrorExpected bool
		ExpectedCode  int
		JSONErrors    bool
		PostAuth      *PostAuth
		Method        string
	}{
		{
			Name: "post-succeed-test",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				d := json.NewDecoder(r.Body)
				var postData PostData
				err := d.Decode(&postData)
				if err != nil {
					w.WriteHeader(http.StatusInternalServerError)
					w.Write([]byte(`{ "exception": "Failed to decode JSON" }`))
				} else if postData.Name != "test" || postData.ID != 5 || !postData.Valid {
					w.WriteHeader(http.StatusInternalServerError)
					w.Write([]byte(`{ "exception": "Decoded JSON is not valid" }`))
				} else {
					w.WriteHeader(http.StatusOK)
					w.Write([]byte("OK"))
				}
			})),
			PostData: &PostData{
				Name:  "test",
				ID:    5,
				Valid: true,
			},
			ErrorExpected: false,
			ExpectedCode:  http.StatusOK,
			JSONErrors:    false,
			PostAuth:      nil,
			Method:        HTTPPost,
		},
		{
			Name: "post-fail-test",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusInternalServerError)
				w.Write([]byte(`{ "exception": "Expected failure" }`))
			})),
			PostData:      &PostData{},
			ErrorExpected: true,
			ExpectedCode:  http.StatusInternalServerError,
			JSONErrors:    false,
			PostAuth:      nil,
			Method:        HTTPPost,
		},
		{
			Name: "post-json-errors-test",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				keys, ok := r.URL.Query()["json_errors"]
				if !ok || len(keys[0]) < 1 {
					w.WriteHeader(http.StatusInternalServerError)
					w.Write([]byte(`{ "exception": "json_errors parameter NOT found!" }`))
				} else {
					w.WriteHeader(http.StatusOK)
					w.Write([]byte("OK"))
				}
			})),
			PostData:      &PostData{},
			ErrorExpected: false,
			ExpectedCode:  http.StatusOK,
			JSONErrors:    true,
			PostAuth:      nil,
			Method:        HTTPPost,
		},
		{
			Name: "post-timeout-test",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				time.Sleep((1 * time.Second) + (500 * time.Millisecond))
				w.WriteHeader(http.StatusOK)
				w.Write([]byte("This request will cause a context timeout"))
			})),
			PostData:      &PostData{},
			ErrorExpected: true,
			ExpectedCode:  -1,
			JSONErrors:    false,
			PostAuth:      nil,
			Method:        HTTPPost,
		},
		{
			Name: "post-auth-test",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				user, pass, ok := r.BasicAuth()
				if ok {
					if user != "testusername" {
						w.WriteHeader(http.StatusUnauthorized)
						w.Write([]byte(`{ "exception": "Bad username!" }`))
					} else if pass != "testpassword" {
						w.WriteHeader(http.StatusUnauthorized)
						w.Write([]byte(`{ "exception": "Bad password!" }`))
					} else {
						w.WriteHeader(http.StatusOK)
						w.Write([]byte("OK"))
					}
				} else {
					w.WriteHeader(http.StatusInternalServerError)
					w.Write([]byte(`{ "exception": "Failed to retrieve auth parameters!" }`))
				}
			})),
			PostData:      &PostData{},
			ErrorExpected: false,
			ExpectedCode:  http.StatusOK,
			JSONErrors:    false,
			PostAuth: &PostAuth{
				Username: "testusername",
				Password: "testpassword",
			},
			Method: HTTPPost,
		},
		{
			Name: "put-test",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				d := json.NewDecoder(r.Body)
				var postData PostData
				err := d.Decode(&postData)
				if err != nil {
					w.WriteHeader(http.StatusInternalServerError)
					w.Write([]byte(`{ "exception": "Failed to decode JSON" }`))
				} else if postData.Name != "test" || postData.ID != 5 || !postData.Valid {
					w.WriteHeader(http.StatusInternalServerError)
					w.Write([]byte(`{ "exception": "Decoded JSON is not valid" }`))
				} else if r.Method != "PUT" {
					w.WriteHeader(http.StatusInternalServerError)
					w.Write([]byte(`{ "exception": "Expected PUT method, received ` + r.Method + `!" }`))
				} else {
					w.WriteHeader(http.StatusOK)
					w.Write([]byte("OK"))
				}
			})),
			PostData: &PostData{
				Name:  "test",
				ID:    5,
				Valid: true,
			},
			ErrorExpected: false,
			JSONErrors:    false,
			ExpectedCode:  http.StatusOK,
			PostAuth:      nil,
			Method:        HTTPPut,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			defer tc.Server.Close()
			testURL, err := url.Parse(tc.Server.URL)
			if err != nil {
				t.Errorf("error parsing url '%s': %+v", tc.Server.URL, err)
			}
			ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
			defer cancel()

			code, err := SendJSON(ctx, testURL, tc.PostData, tc.JSONErrors, tc.PostAuth, tc.Method)

			if err == nil && tc.ErrorExpected {
				t.Errorf("expected error, got nil")
			} else if err != nil && !tc.ErrorExpected {
				t.Errorf("expected no error, got (%+v)", err)
			}

			if code != tc.ExpectedCode {
				t.Errorf("expected code (%d), got (%d)", tc.ExpectedCode, code)
			}
		})
	}
}

type TestOption struct {
	Name  string
	Value string
}

func (t *TestOption) Values() url.Values {
	v := url.Values{}
	v.Set(t.Name, t.Value)
	return v
}

func TestBuildQuery(t *testing.T) {
	testTable := []struct {
		Name   string
		Input  []FetchOption
		Output string
	}{
		{
			Name:   "test-empty-options",
			Input:  []FetchOption{},
			Output: "",
		},
		{
			Name: "test-one-option",
			Input: []FetchOption{
				&TestOption{"hello", "world"},
			},
			Output: "hello=world",
		},
		{
			Name: "test-multiple-options",
			Input: []FetchOption{
				&TestOption{"hello", "world"},
				&TestOption{"this", "test"},
				&TestOption{"abc", "def"},
			},
			Output: "abc=def&hello=world&this=test",
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			output := buildQuery(tc.Input)
			if diff := deep.Equal(output, tc.Output); diff != nil {
				t.Errorf("output not as expected: %+v", diff)
			}
		})
	}
}

func TestFetchWithOptions(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		query := r.URL.Query()
		pairs := []string{}
		for key, values := range query {
			str := key + "="
			for _, value := range values {
				str += value
			}
			pairs = append(pairs, str)
		}
		sort.Strings(pairs)
		for _, value := range pairs {
			w.Write([]byte(value))
			w.Write([]byte(","))
		}
	}))

	testTable := []struct {
		Name         string
		FetchOptions []FetchOption
		Result       []byte
	}{
		{
			Name:         "test-fetch-no-options",
			FetchOptions: []FetchOption{},
			Result:       []byte(""),
		},
		{
			Name: "test-fetch-one-option",
			FetchOptions: []FetchOption{
				&TestOption{"hello", "world"},
			},
			Result: []byte("hello=world,"),
		},
		{
			Name: "test-fetch-multiple-options",
			FetchOptions: []FetchOption{
				&TestOption{"hello", "world"},
				&TestOption{"this", "test"},
				&TestOption{"abc", "def"},
			},
			Result: []byte("abc=def,hello=world,this=test,"),
		},
	}

	defer server.Close()

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			testURL, err := url.Parse(server.URL)
			if err != nil {
				t.Errorf("error parsing url '%s': %+v", server.URL, err)
			}
			ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
			defer cancel()

			body, code, err := FetchWithOptions(ctx, testURL, false, tc.FetchOptions)

			if err != nil {
				t.Errorf("received error (%+v)", err)
			}

			if code != http.StatusOK {
				t.Errorf("received code (%d)", code)
			}

			response, err := io.ReadAll(body)
			if err != nil {
				t.Errorf("unable to extract bytes from response: %+v", err)
			}

			if diff := deep.Equal(response, tc.Result); diff != nil {
				t.Errorf("output not as expected: %+v", diff)
			}
		})
	}
}
