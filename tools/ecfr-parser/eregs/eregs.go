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
	partURL  = "%stitle/%d/existing?json_errors"
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

func post(ctx context.Context, path *url.URL, data interface{}) error {
	start := time.Now()
	buff := bytes.NewBuffer([]byte{})
	enc := json.NewEncoder(buff)
	enc.SetEscapeHTML(false)

	log.Trace("[eregs] Encoding data to JSON")
	if err := enc.Encode(data); err != nil {
		return err
	}

	length := buff.Len()

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, path.String(), buff)
	if err != nil {
		return err
	}

	req.Header.Set("Content-Type", "application/json")
	req.SetBasicAuth(username, password)
	log.Trace("[eregs] Posting to ", path.String())
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		eregsError := &Error{}
		err = json.NewDecoder(resp.Body).Decode(eregsError)
		if err != nil {
			return fmt.Errorf("Received error code %d while posting to %s, unable to extract error message: %+v", resp.StatusCode, path.String(), err)
		}
		return fmt.Errorf("Received error code %d while posting to %s: %s", resp.StatusCode, path.String(), eregsError.Exception)
	}

	log.Trace("[eregs] Posted ", length, " bytes to ", path.String(), " in ", time.Since(start))
	return nil
}

// PostPart is the function that sends a part to the eRegs server
func PostPart(ctx context.Context, p *Part) error {
	path, err := url.Parse(BaseURL)
	if err != nil {
		return err
	}
	return post(ctx, path, p)
}

// PostSupplementalPart is the function that sends a supplemental part to eRegs server
func PostSupplementalPart(ctx context.Context, p ecfr.Part) error {
	path, err := url.Parse(SuppContentURL)
	if err != nil {
		return err
	}
	return post(ctx, path, p)
}

// GetExistingParts gets existing parts already imported
func GetExistingParts(ctx context.Context, title int) (map[string][]string, error) {
	checkURL := fmt.Sprintf(partURL, BaseURL, title)
	log.Trace("[eregs] Beginning checking of existing parts for title ", title, " at ", checkURL)
	start := time.Now()

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, checkURL, nil)
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

	// Cast the body to an array of existing parts
	body := bytes.NewBuffer(b)
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

	log.Trace("[eregs] Checked existing parts for Title ", title, " in ", time.Since(start))
	return result, nil
}
