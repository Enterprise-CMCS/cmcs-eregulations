package eregs

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"

	log "github.com/sirupsen/logrus"
)

// SuppContentURL is the URL of the eRegs service that will accept the post request
var SuppContentURL string

// PostSupplementalPart is the function that sends a supplemental part to eRegs server
func PostSupplementalPart(ctx context.Context, p ecfr.Part) error {
	log.Trace("[eregs] Beginning post of supplemental part ", p.Name, " to ", SuppContentURL)
	start := time.Now()
	buff := bytes.NewBuffer([]byte{})
	enc := json.NewEncoder(buff)
	enc.SetEscapeHTML(false)

	log.Trace("[eregs] Encoding supplemental part ", p.Name, " to JSON")
	if err := enc.Encode(p); err != nil {
		return err
	}

	length := buff.Len()

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, SuppContentURL, buff)
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	req.SetBasicAuth(username, password)
	log.Trace("[eregs] Posting supplemental part ", p.Name)
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		return fmt.Errorf("received error code %d while posting supplemental part ", resp.StatusCode)
	}

	log.Trace("[eregs] Posted ", length, " bytes for supplemental part ", p.Name, " in ", time.Since(start))
	return nil
}
