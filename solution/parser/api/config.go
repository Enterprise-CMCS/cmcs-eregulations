package api

import (
	"context"
	"encoding/json"
	"fmt"
	"strconv"
	"strings"
	"time"

	log "github.com/sirupsen/logrus"
)

var configURL = "/parser_config"

// SubchapterArg is an array of type string
type SubchapterArg []string

func (sc *SubchapterArg) String() string {
	return strings.Join(*sc, "-")
}

// Set is to validate and set the subchapter
func (sc *SubchapterArg) Set(s string) error {
	*sc = strings.Split(s, "-")
	if len(*sc) != 2 || strings.TrimSpace((*sc)[0]) == "" || strings.TrimSpace((*sc)[1]) == "" {
		return fmt.Errorf("subchapter is expected to be of the form <Roman Numeral>-<Letter>")
	}
	return nil
}

// SubchapterList is an array of SubchapterArgs
type SubchapterList []SubchapterArg

// PartList is an array of strings representing parts
type PartList []string

// UnmarshalText extracts subchapters (e.g. IV-C) from a provided comma-separated list
func (sl *SubchapterList) UnmarshalText(data []byte) error {
	subchapters := strings.Split(string(data), ",")
	*sl = make([]SubchapterArg, 0, len(subchapters))
	for _, subchapter := range subchapters {
		if len(subchapter) > 0 {
			var sc SubchapterArg
			err := sc.Set(strings.TrimSpace(subchapter))
			if err != nil {
				return err
			}
			*sl = append(*sl, sc)
		}
	}
	return nil
}

// UnmarshalText extracts valid parts (must be numeric) and stores as strings
func (pl *PartList) UnmarshalText(data []byte) error {
	tmp := strings.Split(string(data), ",")
	*pl = make([]string, 0, len(tmp))
	for _, raw := range tmp {
		trimmed := strings.TrimSpace(raw)
		_, err := strconv.Atoi(trimmed)
		if err != nil {
			log.Error("[config] ", trimmed, " is not a valid part, skipping.")
			continue
		}
		*pl = append(*pl, trimmed)
	}
	return nil
}

// TitleConfig represents parser configuration for a specific title, i.e. what parts to parse
type TitleConfig struct {
	Title       int            `json:"title"`
	Subchapters SubchapterList `json:"subchapters"`
	Parts       PartList       `json:"parts"`
}

// ParserConfig represents configuration for the parser as a whole
type ParserConfig struct {
	Workers            int            `json:"workers"`
	Retries            int            `json:"retries"`
	LogLevel           string         `json:"loglevel"`
	UploadSupplemental bool           `json:"upload_supplemental_locations"`
	LogParseErrors     bool           `json:"log_parse_errors"`
	SkipRegVersions    bool           `json:"skip_reg_versions"`
	SkipFRDocuments    bool           `json:"skip_fr_documents"`
	Titles             []*TitleConfig `json:"titles"`
}

// RetrieveConfig fetches parser config from eRegs at /v3/parser_config
func RetrieveConfig() (*ParserConfig, int, error) {
	log.Debug("[config] Retrieving parser configuration from ", configURL)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	body, code, err := Get(ctx, configURL)
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
