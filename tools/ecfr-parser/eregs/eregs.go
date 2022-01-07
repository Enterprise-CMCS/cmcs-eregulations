package eregs

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"path"
	"time"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/parsexml"

	log "github.com/sirupsen/logrus"
)

// BaseURL is the URL of the eRegs service that will accept the post requests
var BaseURL string

// SuppContentURL is the URL of the eRegs service that will accept the post request
var SuppContentURL string

var client = &http.Client{
	Transport: &http.Transport{},
}

var (
	username = os.Getenv("EREGS_USERNAME")
	password = os.Getenv("EREGS_PASSWORD")
	partURL  = "/title/%d/existing"
)

// Part is the struct used to send a part to the eRegs server
type Part struct {
	Title     int             `json:"title,string" xml:"-"`
	Name      string          `json:"name" xml:"-"`
	Date      string          `json:"date" xml:"-"`
	Structure *ecfr.Structure `json:"structure" xml:"-"`
	Document  *parsexml.Part  `json:"document"`
	Processed bool
}

// Error message returned by eRegs as JSON (if ?json_errors appended)
type Error struct {
	Status    string   `json:"status"`
	Type      string   `json:"type"`
	Exception string   `json:"exception"`
	Traceback []string `json:"traceback"`
}

// ExistingPart is a regulation that has been loaded already
type ExistingPart struct {
	Date     string   `json:"date"`
	PartName []string `json:"partName"`
}

func post(ctx context.Context, eregsPath *url.URL, data interface{}) error {
	q := eregsPath.Query()
	q.Add("json_errors", "true")
	eregsPath.RawQuery = q.Encode()

	start := time.Now()
	buff := bytes.NewBuffer([]byte{})
	enc := json.NewEncoder(buff)
	enc.SetEscapeHTML(false)

	log.Trace("[eregs] Encoding data to JSON")
	if err := enc.Encode(data); err != nil {
		return err
	}

	length := buff.Len()

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, eregsPath.String(), buff)
	if err != nil {
		return err
	}

	req.Header.Set("Content-Type", "application/json")
	req.SetBasicAuth(username, password)
	log.Trace("[eregs] Posting to ", eregsPath.String())
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		eregsError := &Error{}
		err = json.NewDecoder(resp.Body).Decode(eregsError)
		if err != nil {
			return fmt.Errorf("Received error code %d while posting to %s, unable to extract error message: %+v", resp.StatusCode, eregsPath.String(), err)
		}
		return fmt.Errorf("Received error code %d while posting to %s: %s", resp.StatusCode, eregsPath.String(), eregsError.Exception)
	}

	log.Trace("[eregs] Posted ", length, " bytes to ", eregsPath.String(), " in ", time.Since(start))
	return nil
}

// PostPart is the function that sends a part to the eRegs server
func PostPart(ctx context.Context, p *Part) error {
	eregsPath, err := url.Parse(BaseURL)
	if err != nil {
		return err
	}
	return post(ctx, eregsPath, p)
}

// PostSupplementalPart is the function that sends a supplemental part to eRegs server
func PostSupplementalPart(ctx context.Context, p ecfr.Part) error {
	eregsPath, err := url.Parse(SuppContentURL)
	if err != nil {
		return err
	}
	return post(ctx, eregsPath, p)
}

func fetch(ctx context.Context, url *url.URL) (io.Reader, error) {

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url.String(), nil)
	if err != nil {
		return nil, err
	}

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		eregsError := &Error{}
		err = json.NewDecoder(resp.Body).Decode(eregsError)
		if err != nil {
			return nil, fmt.Errorf("Received error code %d while checking, unable to extract error message: %+v", resp.StatusCode, err)
		}
		return nil, fmt.Errorf("Received error code %d while checking: %s", resp.StatusCode, eregsError.Exception)
	}

	// Read the body
	b, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("Unable to read response body while checking existing versions: %+v", err)
	}
	body := bytes.NewBuffer(b)

	return body, nil
}

// GetExistingParts gets existing parts already imported
func GetExistingParts(ctx context.Context, title int) (map[string][]string, error) {
	checkURL, err := url.Parse(BaseURL)
	if err != nil {
		return nil, err
	}
	q := checkURL.Query()
	q.Add("json_errors", "true")
	checkURL.RawQuery = q.Encode()
	checkURL.Path = path.Join(checkURL.Path, fmt.Sprintf(partURL, title))

	log.Trace("[eregs] Beginning checking of existing parts for title ", title, " at ", checkURL.String())

	body, err := fetch(ctx, checkURL)
	if err != nil {
		return nil, err
	}

	// Cast the body to an array of existing parts
	var vs []ExistingPart
	d := json.NewDecoder(body)
	if err := d.Decode(&vs); err != nil {
		return nil, fmt.Errorf("Unable to decode response body while checking existing versions: %+v", err)
	}

	// reduce the results to the desired format
	result := make(map[string][]string)
	for _, ep := range vs {
		result[ep.Date] = ep.PartName
	}

	return result, nil
}
