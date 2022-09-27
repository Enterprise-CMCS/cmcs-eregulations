package eregs

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/cmsgov/cmcs-eregulations/lib/ecfr"

	"github.com/go-test/deep"
)

func TestPostParserResult(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/ecfr_parser_result/42" {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte("OK"))
		} else {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte("BAD PATH"))
		}
	}))
	defer server.Close()
	BaseURL = server.URL

	result := ParserResult{
		Start:           time.Now().Format(time.RFC3339),
		Title:           42,
		Parts:           "1,2,3",
		Subchapters:     "A,B,C",
		Workers:         3,
		Errors:          0,
		TotalVersions:   100,
		SkippedVersions: 99,
	}

	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()

	code, err := PostParserResult(ctx, &result)

	if err != nil {
		t.Errorf("received error (%+v)", err)
	}

	if code != http.StatusOK {
		t.Errorf("received code (%d)", code)
	}
}