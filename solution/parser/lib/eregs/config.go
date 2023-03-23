package eregs

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/cmsgov/cmcs-eregulations/lib/ecfr"
	"github.com/cmsgov/cmcs-eregulations/lib/network"

	log "github.com/sirupsen/logrus"
)

var configURL = "/parser_config"

// PartConfig represents parser configuration for a specific title and subchapter/part combo
type PartConfig struct {
	Title           int    `json:"title"`
	Type            string `json:"type"`
	Value           string `json:"value"`
	UploadRegText   bool   `json:"upload_reg_text"`
	UploadLocations bool   `json:"upload_locations"`
	UploadFRDocs    bool   `json:"upload_fr_docs"`
}

// ParserConfig represents configuration for the parser as a whole
type ParserConfig struct {
	Workers            int           `json:"workers"`
	Retries            int           `json:"retries"`
	LogLevel           string        `json:"loglevel"`
	UploadSupplemental bool          `json:"upload_supplemental_locations"`
	LogParseErrors     bool          `json:"log_parse_errors"`
	SkipRegVersions    bool          `json:"skip_reg_versions"`
	SkipFRDocuments    bool          `json:"skip_fr_documents"`
	Parts              []*PartConfig `json:"parts"`
}

// RetrieveConfig fetches parser config from eRegs at /v3/parser_config
func RetrieveConfig() (*ParserConfig, int, error) {
	u, err := parseURL(configURL)
	if err != nil {
		return nil, -1, fmt.Errorf("%s is not a valid URL! Please correctly set the EREGS_API_URL_V3 environment variable", BaseURL)
	}

	log.Debug("[config] Retrieving parser configuration from ", u.String())

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	body, code, err := network.Fetch(ctx, u, true)
	if err != nil {
		return nil, code, err
	}

	var config ParserConfig
	d := json.NewDecoder(body)
	if err := d.Decode(&config); err != nil {
		return nil, code, fmt.Errorf("unable to decode configuration from response body: %+v", err)
	}

	return &config, code, nil
}

// GetLogLevel converts a string (e.g. "warn") to a log level (e.g. log.WarnLevel)
func GetLogLevel(l string) log.Level {
	switch l {
	case "warn":
		return log.WarnLevel
	case "fatal":
		return log.FatalLevel
	case "error":
		return log.ErrorLevel
	case "info":
		return log.InfoLevel
	case "debug":
		return log.DebugLevel
	case "trace":
		return log.TraceLevel
	default:
		log.Warn("[main] '", l, "' is an invalid log level, defaulting to 'warn'.")
		return log.WarnLevel
	}
}

var extractSubchapterPartsFunc = ecfr.ExtractSubchapterParts

// ProcessPartsList converts parts and subchapters into just parts
func ProcessPartsList(ctx context.Context, title int, rawParts []*PartConfig) ([]*PartConfig, error) {
	var parts []*PartConfig
	for _, part := range rawParts {
		if part.Type == "part" {
			parts = append(parts, part)
		} else if part.Type == "subchapter" {
			log.Debug("[main] Fetching parts list for title ", title, " subchapter", part.Value)
			subchapter := strings.Split(part.Value, "-")
			subchapterParts, err := extractSubchapterPartsFunc(ctx, title, &ecfr.SubchapterOption{subchapter[0], subchapter[1]})
			if err != nil {
				return nil, err
			}
			for _, subchapterPart := range subchapterParts {
				parts = append(parts, &PartConfig{
					Type:            "part",
					Title:           part.Title,
					Value:           subchapterPart,
					UploadLocations: part.UploadLocations,
					UploadRegText:   part.UploadRegText,
					UploadFRDocs:    part.UploadFRDocs,
				})
			}
		} else {
			return nil, fmt.Errorf("%s is not a valid type for %s", part.Type, part.Value)
		}
	}

	if len(parts) < 1 {
		return nil, fmt.Errorf("some number of parts must be specified")
	}

	return parts, nil
}
