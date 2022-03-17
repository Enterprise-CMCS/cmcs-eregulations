package network

import (
	"net/http"
	"net/url"
	"time"
	"bytes"
	"fmt"
	"context"
	"encoding/json"
	"os"
	"io"

	log "github.com/sirupsen/logrus"
)

const timeout = 10 * time.Second

var client = &http.Client{
	Transport: &http.Transport{},
}

// PostAuth defines the username and password to be used during HTTP POST attempts
type PostAuth struct {
	Username string
	Password string
}

// Error message returned by eRegs as JSON (if ?json_errors appended)
type Error struct {
	Status    string   `json:"status"`
	Type      string   `json:"type"`
	Exception string   `json:"exception"`
	Traceback []string `json:"traceback"`
}

const (
	HttpPost string = http.MethodPost
	HttpPut string = http.MethodPut
)

// SendJSON attempts to send arbitrary JSON data to a given URL using a specified method
func SendJSON(ctx context.Context, postURL *url.URL, data interface{}, jsonErrors bool, auth *PostAuth, method string) error {
	if jsonErrors {
		q := postURL.Query()
		q.Add("json_errors", "true")
		postURL.RawQuery = q.Encode()
	}
	postPath := postURL.String()

	log.Trace("[network] Beginning ", method, " to ", postPath)
	start := time.Now()
	buff := bytes.NewBuffer([]byte{})
	enc := json.NewEncoder(buff)
	enc.SetEscapeHTML(false)

	log.Trace("[network] Encoding data as JSON")
	if err := enc.Encode(data); err != nil {
		return fmt.Errorf("Failed to encode data as JSON: %+v", err)
	}

	length := buff.Len()

	req, err := http.NewRequestWithContext(ctx, method, postPath, buff)
	if err != nil {
		return fmt.Errorf("Failed to create HTTP request: %+v", err)
	}

	req.Header.Set("User-Agent", "eRegs for "+os.Getenv("NAME"))
	req.Header.Set("Content-Type", "application/json")
	if auth != nil {
		req.SetBasicAuth(auth.Username, auth.Password)
	}
	log.Trace("[network] ", method, "ing data to ", postPath)
	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("%s failed to complete: %+v", method, err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		postError := &Error{}
		err = json.NewDecoder(resp.Body).Decode(postError)
		if err != nil {
			return fmt.Errorf("Received error code %d while %sing to %s, unable to extract error message: %+v", resp.StatusCode, method, postPath, err)
		}
		return fmt.Errorf("Received error code %d while %sing to %s: %s", resp.StatusCode, method, postPath, postError.Exception)
	}

	log.Trace("[network] ", method, "ed ", length, " bytes to ", postPath, " in ", time.Since(start))
	return nil
}

// Fetch attempts to fetch arbitrary bytes from a given URL
func Fetch(ctx context.Context, fetchURL *url.URL, jsonErrors bool) (io.Reader, error) {
	if jsonErrors {
		q := fetchURL.Query()
		q.Add("json_errors", "true")
		fetchURL.RawQuery = q.Encode()
	}
	fetchPath := fetchURL.String()

	log.Trace("[network] Beginning fetch from ", fetchPath)
	start := time.Now()

	c, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	req, err := http.NewRequestWithContext(c, http.MethodGet, fetchPath, nil)
	if err != nil {
		return nil, fmt.Errorf("Failed to create HTTP request: %+v", err)
	}

	req.Header.Set("User-Agent", "eRegs for "+os.Getenv("NAME"))
	log.Trace("[network] Fetching from ", fetchPath)
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("Fetch failed to complete: %+v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		fetchError := &Error{}
		err = json.NewDecoder(resp.Body).Decode(fetchError)
		if err != nil {
			return nil, fmt.Errorf("Received error code %d while fetching from %s, unable to extract error message: %+v", resp.StatusCode, fetchPath, err)
		}
		return nil, fmt.Errorf("Received error code %d while fetching from %s: %s", resp.StatusCode, fetchPath, fetchError.Exception)
	}

	b, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("Failed to read response body: %+v", err)
	}
	body := bytes.NewBuffer(b)

	log.Trace("[network] Received ", len(b), " bytes from ", fetchPath, " in ", time.Since(start))
	return body, nil
}

// FetchOption defines optional values for the fetch process
type FetchOption interface {
	Values() url.Values
}

func buildQuery(opts []FetchOption) string {
	q := url.Values{}
	for _, opt := range opts {
		v := opt.Values()
		for key := range v {
			q.Set(key, v.Get(key))
		}
	}
	return q.Encode()
}

// FetchWithOptions attempts to fetch arbitrary bytes from a given URL with provided fetch options
func FetchWithOptions(ctx context.Context, fetchURL *url.URL, jsonErrors bool, opts []FetchOption) (io.Reader, error) {
	fetchURL.RawQuery = buildQuery(opts)
	return Fetch(ctx, fetchURL, jsonErrors)
}
