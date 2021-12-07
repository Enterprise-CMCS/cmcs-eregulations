package eregs

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/parsexml"

	log "github.com/sirupsen/logrus"
)

// BaseURL is the URL of the eRegs service that will accept the post requests
var BaseURL string

var client = &http.Client{
	Transport: &http.Transport{},
}

var (
	username = os.Getenv("EREGS_USERNAME")
	password = os.Getenv("EREGS_PASSWORD")
	partURL = "%stitle/%d/existing"
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

// ExistingPart is a regulation that has been loaded already
type ExistingPart struct {
	Date     string   `json:"date"`
	PartName []string `json:"partName"`
}

// PostPart is the function that sends a part to the eRegs server
func PostPart(ctx context.Context, p *Part) error {
	log.Trace("[eregs] Beginning post of part ", p.Name, " version ", p.Date, " to ", BaseURL)
	start := time.Now()

	buff := bytes.NewBuffer([]byte{})
	enc := json.NewEncoder(buff)
	enc.SetEscapeHTML(false)

	log.Trace("[eregs] Encoding part ", p.Name, " version ", p.Date, " to JSON")
	if err := enc.Encode(p); err != nil {
		return err
	}

	length := buff.Len()

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, BaseURL, buff)
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	req.SetBasicAuth(username, password)
	log.Trace("[eregs] Posting part ", p.Name)
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		return fmt.Errorf("Received error code %d while posting", resp.StatusCode)
	}

	log.Trace("[eregs] Posted ", length, " bytes for part ", p.Name, " version ", p.Date, " in ", time.Since(start))
	return nil
}

func GetExistingParts(ctx context.Context, title int) (map[string][]string, error){
    checkUrl := fmt.Sprintf(partURL, BaseURL, title)
    log.Trace("[eregs] Beginning checking of existing parts at ", checkUrl)
	start := time.Now()

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, checkUrl, nil)
	if err != nil {
	    log.Trace(err)
		return nil, err
	}

	log.Trace("[eregs] Checking title ", title)
	resp, err := client.Do(req)
	if err != nil {
	    log.Trace(err)
		return nil, err
	}
	defer resp.Body.Close()
    if resp.StatusCode >= 400 {
		log.Trace(fmt.Errorf("Received error code %d while checking", resp.StatusCode))
		return nil, err
	}

	// Read the body
	b, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("from `io.ReadAll`: %+v", err)
	}

	// Cast the body to an array of existing parts
	body := bytes.NewBuffer(b)
	var vs []ExistingPart
	d := json.NewDecoder(body)
	if err := d.Decode(&vs); err != nil {
		return nil, err
	}

    // reduce the results to the desired format
    result := make(map[string][]string)
    for _, ep := range vs{
        result[ep.Date] = ep.PartName
    }

	log.Trace("[eregs] Checked existing parts for Title ", title , " in ", time.Since(start))
	return result, nil
}