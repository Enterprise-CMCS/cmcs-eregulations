package eregs

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/parseXML"

	log "github.com/sirupsen/logrus"
)

var BaseURL string

var client = &http.Client{
	Transport: &http.Transport{},
}

var (
	username = os.Getenv("EREGS_USERNAME")
	password = os.Getenv("EREGS_PASSWORD")
)

type Part struct {
	Title     int             `json:"title,string" xml:"-"`
	Name      string          `json:"name" xml:"-"`
	Date      string          `json:"date" xml:"-"`
	Structure *ecfr.Structure `json:"structure" xml:"-"`
	Document  *parseXML.Part  `json:"document"`
}

func PostPart(ctx context.Context, p *Part) (*http.Response, error) {
	log.Trace("[eregs] Beginning post of part ", p.Name, " version ", p.Date, " to ", BaseURL)
	start := time.Now()

	buff := bytes.NewBuffer([]byte{})
	enc := json.NewEncoder(buff)
	enc.SetEscapeHTML(false)

	log.Trace("[eregs] Encoding part ", p.Name, " version ", p.Date, " to JSON")
	if err := enc.Encode(p); err != nil {
		return nil, err
	}

	length := buff.Len()

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, BaseURL, buff)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	req.SetBasicAuth(username, password)
	log.Trace("[eregs] Posting part ", p.Name)
	resp, err := client.Do(req)
	if err != nil {
		return resp, err
	}

	if resp.StatusCode >= 400 {
		return resp, fmt.Errorf("%d", resp.StatusCode)
	}

	log.Trace("[eregs] Posted ", length, " bytes for part ", p.Name, " version ", p.Date, " in ", time.Since(start))
	return resp, nil
}
