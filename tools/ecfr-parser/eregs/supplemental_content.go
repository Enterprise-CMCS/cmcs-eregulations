package eregs

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
)

var SuppContentURL string

type SuppContentPart struct {
	Sections *ecfr.Section `json:"section"`
	Subparts *ecfr.Subpart `json:"subpart"`
}

func PostSupplementalPart(ctx context.Context, p *SuppContentPart) (*http.Response, error) {
	buff := bytes.NewBuffer([]byte{})
	enc := json.NewEncoder(buff)
	enc.SetEscapeHTML(false)

	if err := enc.Encode(p); err != nil {
		return nil, err
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, SuppContentURL, buff)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	req.SetBasicAuth(username, password)
	resp, err := client.Do(req)
	if err != nil {
		return resp, err
	}

	if resp.StatusCode >= 400 {
		return resp, fmt.Errorf("%d", resp.StatusCode)
	}
	return resp, nil
}
