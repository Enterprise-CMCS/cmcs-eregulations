package network

import (
	"testing"
	"net/http/httptest"
	"net/http"
	"net/url"
	"context"
	"time"
	"reflect"
	"io"
	"encoding/json"
	"sort"
)

func TestFetch(t *testing.T) {
	testTable := []struct {
		Name string
		Server *httptest.Server
		ExpectedResponse []byte
		ErrorExpected bool
		JSONErrors bool
	}{
		{
			Name: "fetch-succeed-test",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusOK)
				w.Write([]byte(`This is an arbitrary array of bytes`))
			})),
			ExpectedResponse: []byte(`This is an arbitrary array of bytes`),
			ErrorExpected: false,
			JSONErrors: false,
		},
		{
			Name: "fetch-fail-test",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusInternalServerError)
				w.Write([]byte(`This request failed`))
			})),
			ExpectedResponse: nil,
			ErrorExpected: true,
			JSONErrors: false,
		},
		{
			Name: "fetch-json-errors-test",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusOK)
				keys, ok := r.URL.Query()["json_errors"]
				if !ok || len(keys[0]) < 1 {
					w.Write([]byte(`json_errors parameter NOT found!`))
				} else {
					w.Write([]byte(`json_errors parameter found!`))
				}
			})),
			ExpectedResponse: []byte(`json_errors parameter found!`),
			ErrorExpected: false,
			JSONErrors: true,
		},
		{
			Name: "fetch-timeout-test",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				time.Sleep((1 * time.Second) + (500 * time.Millisecond))
				w.WriteHeader(http.StatusOK)
				w.Write([]byte(`This request will cause a context timeout`))
			})),
			ExpectedResponse: nil,
			ErrorExpected: true,
			JSONErrors: false,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			defer tc.Server.Close()
			testURL, err := url.Parse(tc.Server.URL)
			if err != nil {
				t.Errorf("error parsing url \"%s\": %+v", tc.Server.URL, err)
			}
			ctx, cancel := context.WithTimeout(context.Background(), 1 * time.Second)
			defer cancel()

			body, err := Fetch(ctx, testURL, tc.JSONErrors)

			if err == nil && tc.ErrorExpected {
				t.Errorf("expected error, got nil")
			} else if err != nil && !tc.ErrorExpected {
				t.Errorf("expected no error, got (%+v)", err)
			}
			if body != nil {
				response, err := io.ReadAll(body)
				if err != nil {
					t.Errorf("unable to extract bytes from response: %+v", err)
				}
				if !reflect.DeepEqual(response, tc.ExpectedResponse) {
					t.Errorf("expected (%s), got (%s)", tc.ExpectedResponse, response)
				}
			} else if tc.ExpectedResponse != nil {
				t.Errorf("expected (%s), got nil", tc.ExpectedResponse)
			}
		})
	}
}

type PostData struct {
	Name   string `json:"name"`
	ID     int    `json:"id"`
	Valid  bool   `json:"yes"`
}

func TestPostJSON(t *testing.T) {
	testTable := []struct {
		Name string
		Server *httptest.Server
		PostData *PostData
		ErrorExpected bool
		JSONErrors bool
		PostAuth *PostAuth
	}{
		{
			Name: "post-succeed-test",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				d := json.NewDecoder(r.Body)
				var postData PostData
				err := d.Decode(&postData)
				if err != nil {
					w.WriteHeader(http.StatusInternalServerError)
					w.Write([]byte(`Failed to decode JSON`))
				} else if postData.Name != "test" || postData.ID != 5 || !postData.Valid {
					w.WriteHeader(http.StatusInternalServerError)
					w.Write([]byte(`Decoded JSON is not valid`))
				} else {
					w.WriteHeader(http.StatusOK)
					w.Write([]byte(`OK`))
				}
			})),
			PostData: &PostData{
				Name: "test",
				ID: 5,
				Valid: true,
			},
			ErrorExpected: false,
			JSONErrors: false,
			PostAuth: nil,
		},
		{
			Name: "post-fail-test",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusInternalServerError)
				w.Write([]byte(`Expected failure`))
			})),
			PostData: &PostData{},
			ErrorExpected: true,
			JSONErrors: false,
			PostAuth: nil,
		},
		{
			Name: "post-json-errors-test",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				keys, ok := r.URL.Query()["json_errors"]
				if !ok || len(keys[0]) < 1 {
					w.WriteHeader(http.StatusInternalServerError)
					w.Write([]byte(`json_errors parameter NOT found!`))
				} else {
					w.WriteHeader(http.StatusOK)
					w.Write([]byte(`json_errors parameter found!`))
				}
			})),
			PostData: &PostData{},
			ErrorExpected: false,
			JSONErrors: true,
			PostAuth: nil,
		},
		{
			Name: "post-timeout-test",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				time.Sleep((1 * time.Second) + (500 * time.Millisecond))
				w.WriteHeader(http.StatusOK)
				w.Write([]byte(`This request will cause a context timeout`))
			})),
			PostData: &PostData{},
			ErrorExpected: true,
			JSONErrors: false,
			PostAuth: nil,
		},
		{
			Name: "post-auth-test",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				user, pass, ok := r.BasicAuth()
				if ok {
					if user != "testusername" {
						w.WriteHeader(http.StatusUnauthorized)
						w.Write([]byte(`Bad username!`))
					} else if pass != "testpassword" {
						w.WriteHeader(http.StatusUnauthorized)
						w.Write([]byte(`Bad password!`))
					} else {
						w.WriteHeader(http.StatusOK)
						w.Write([]byte(`OK`))
					}
				} else {
					w.WriteHeader(http.StatusInternalServerError)
					w.Write([]byte(`Failed to retrieve auth parameters!`))
				}
			})),
			PostData: &PostData{},
			ErrorExpected: false,
			JSONErrors: false,
			PostAuth: &PostAuth{
				Username: "testusername",
				Password: "testpassword",
			},
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			defer tc.Server.Close()
			testURL, err := url.Parse(tc.Server.URL)
			if err != nil {
				t.Errorf("error parsing url \"%s\": %+v", tc.Server.URL, err)
			}
			ctx, cancel := context.WithTimeout(context.Background(), 1 * time.Second)
			defer cancel()

			err = PostJSON(ctx, testURL, tc.PostData, tc.JSONErrors, tc.PostAuth)

			if err == nil && tc.ErrorExpected {
				t.Errorf("expected error, got nil")
			} else if err != nil && !tc.ErrorExpected {
				t.Errorf("expected no error, got (%+v)", err)
			}
		})
	}
}

type TestOption struct {
	Name string
	Value string
}

func (t *TestOption) Values() url.Values {
	v := url.Values{}
	v.Set(t.Name, t.Value)
	return v
}

func TestBuildQuery(t *testing.T) {
	testTable := []struct {
		Name string
		Input []FetchOption
		Output string
	}{
		{
			Name: "test-empty-options",
			Input: []FetchOption{},
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
			if !reflect.DeepEqual(output, tc.Output) {
				t.Errorf("expect (%s), got (%s)", tc.Output, output)
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
		Name string
		FetchOptions []FetchOption
		Result []byte
	}{
		{
			Name: "test-fetch-no-options",
			FetchOptions: []FetchOption{},
			Result: []byte(""),
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
				t.Errorf("error parsing url \"%s\": %+v", server.URL, err)
			}
			ctx, cancel := context.WithTimeout(context.Background(), 1 * time.Second)
			defer cancel()

			body, err := FetchWithOptions(ctx, testURL, false, tc.FetchOptions)

			if err != nil {
				t.Errorf("received error (%+v)", err)
			}

			response, err := io.ReadAll(body)
			if err != nil {
				t.Errorf("unable to extract bytes from response: %+v", err)
			}

			if !reflect.DeepEqual(response, tc.Result) {
				t.Errorf("expected (%s), received (%s)", tc.Result, response)
			}
		})
	}
}
