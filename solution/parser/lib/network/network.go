package network

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"time"

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

// Represents HTTP POST and PUT methods
const (
	HTTPPost string = http.MethodPost
	HTTPPut  string = http.MethodPut
)

// SendJSON attempts to send arbitrary JSON data to a given URL using a specified method
func SendJSON(ctx context.Context, postURL *url.URL, data interface{}, jsonErrors bool, auth *PostAuth, method string) (int, error) {
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
		return -1, fmt.Errorf("failed to encode data as JSON: %+v", err)
	}

	length := buff.Len()

	req, err := http.NewRequestWithContext(ctx, method, postPath, buff)
	if err != nil {
		return -1, fmt.Errorf("failed to create HTTP request: %+v", err)
	}

	req.Header.Set("User-Agent", "Policy Connector for "+os.Getenv("NAME"))
	req.Header.Set("Content-Type", "application/json")
	if auth != nil {
		req.SetBasicAuth(auth.Username, auth.Password)
	}
	log.Trace("[network] ", method, "ing data to ", postPath)
	resp, err := client.Do(req)
	if err != nil {
		return -1, fmt.Errorf("%s failed to complete: %+v", method, err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		postError := &Error{}
		bodyBytes, err := io.ReadAll(resp.Body)
		if err != nil {
			return resp.StatusCode, fmt.Errorf("received error code %d while %sing to %s, unable to extract error message", resp.StatusCode, method, postPath)
		}
		err = json.NewDecoder(bytes.NewReader(bodyBytes)).Decode(postError)
		if err != nil {
			return resp.StatusCode, fmt.Errorf("received error code %d while %sing to %s, unable to extract error message: %+v", resp.StatusCode, method, postPath, err)
		} else if postError.Exception == "" {
			return resp.StatusCode, fmt.Errorf("received error code %d while %sing to %s, unable to extract error message. Response body: %s", resp.StatusCode, method, postPath, string(bodyBytes))
		}
		return resp.StatusCode, fmt.Errorf("received error code %d while %sing to %s: %s", resp.StatusCode, method, postPath, postError.Exception)
	}

	log.Trace("[network] ", method, "ed ", length, " bytes to ", postPath, " in ", time.Since(start))
	return resp.StatusCode, nil
}

// Fetch attempts to fetch arbitrary bytes from a given URL
func Fetch(ctx context.Context, fetchURL *url.URL, jsonErrors bool, auth *PostAuth) (io.Reader, int, error) {
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
		return nil, -1, fmt.Errorf("failed to create HTTP request: %+v", err)
	}

	req.Header.Set("User-Agent", "Policy Connector for "+os.Getenv("NAME"))
	if auth != nil {
		req.SetBasicAuth(auth.Username, auth.Password)
	}

	log.Trace("[network] Fetching from ", fetchPath)
	resp, err := client.Do(req)
	if err != nil {
		return nil, -1, fmt.Errorf("fetch failed to complete: %+v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		fetchError := &Error{}
		bodyBytes, err := io.ReadAll(resp.Body)
		if err != nil {
			return nil, resp.StatusCode, fmt.Errorf("received error code %d while fetching from %s, unable to extract error message", resp.StatusCode, fetchPath)
		}
		err = json.NewDecoder(bytes.NewReader(bodyBytes)).Decode(fetchError)
		if err != nil {
			return nil, resp.StatusCode, fmt.Errorf("received error code %d while fetching from %s, unable to extract error message: %+v", resp.StatusCode, fetchPath, err)
		} else if fetchError.Exception == "" {
			return nil, resp.StatusCode, fmt.Errorf("received error code %d while fetching from %s, unable to extract error message. Response body: %s", resp.StatusCode, fetchPath, string(bodyBytes))
		}
		return nil, resp.StatusCode, fmt.Errorf("received error code %d while fetching from %s: %s", resp.StatusCode, fetchPath, fetchError.Exception)
	}

	b, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, resp.StatusCode, fmt.Errorf("failed to read response body: %+v", err)
	}
	body := bytes.NewBuffer(b)

	log.Trace("[network] Received ", len(b), " bytes from ", fetchPath, " in ", time.Since(start))
	return body, resp.StatusCode, nil
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
func FetchWithOptions(ctx context.Context, fetchURL *url.URL, jsonErrors bool, opts []FetchOption, auth *PostAuth) (io.Reader, int, error) {
	fetchURL.RawQuery = buildQuery(opts)
	return Fetch(ctx, fetchURL, jsonErrors, auth)
}
