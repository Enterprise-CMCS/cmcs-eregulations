package eregs

import (
	"context"
	"fmt"
	"net/url"
	"os"
	"path"
	"time"

	"github.com/cmsgov/cmcs-eregulations/lib/network"
)

// BaseURL is the URL of the eRegs service that will accept the post requests
var BaseURL string

// DefaultBaseURL is the default eRegs API URL to use if none is specified
var DefaultBaseURL = "http://localhost:8000/v3/"

var parserResultURL = "/ecfr_parser_result/%d"

var PostAuth = &network.PostAuth{
	Username: os.Getenv("EREGS_USERNAME"),
	Password: os.Getenv("EREGS_PASSWORD"),
}

func getAuth() *network.PostAuth {
	stageEnv := os.Getenv("STAGE_ENV")
	if stageEnv == "" || stageEnv == "local" || stageEnv == "prod" {
		return nil
	}
	return PostAuth
}

func init() {
	BaseURL = os.Getenv("EREGS_API_URL_V3")
	if BaseURL == "" {
		BaseURL = DefaultBaseURL
	}
}

func parseURL(apiPath string) (*url.URL, error) {
	u, err := url.Parse(BaseURL)
	if err != nil {
		return nil, err
	}
	u.Path = path.Join(u.Path, apiPath)
	return u, nil
}

// ParserResult is the struct used to send results to the eRegs server
type ParserResult struct {
	Title           int    `json:"title,string"`
	Start           string `json:"start"`
	End             string `json:"end"`
	Workers         int    `json:"workers,string"`
	Parts           string `json:"parts"`
	Subchapters     string `json:"subchapters"`
	SkippedVersions int    `json:"skippedVersions,string"`
	TotalVersions   int    `json:"totalVersions,string"`
	Errors          int    `json:"errors,string"`
}

// PostParserResult is the function that sends a parser result to the eRegs server
func PostParserResult(ctx context.Context, p *ParserResult) (int, error) {
	u, err := parseURL(fmt.Sprintf(parserResultURL, p.Title))
	if err != nil {
		return -1, err
	}
	p.End = time.Now().Format(time.RFC3339)
	return network.SendJSON(ctx, u, p, true, PostAuth, network.HTTPPost)
}
