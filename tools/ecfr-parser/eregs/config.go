package eregs

import (
	"fmt"
	"net/url"
	"context"
	"path"
	"strings"
	"time"
	"strconv"
	"encoding/json"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/network"

	log "github.com/sirupsen/logrus"
)

// SubchapterArg is an array of type string
type SubchapterArg []string

func (sc *SubchapterArg) String() string {
	return strings.Join(*sc, "-")
}

// Set is to validate and set the subchapter
func (sc *SubchapterArg) Set(s string) error {
	*sc = strings.Split(s, "-")
	if len(*sc) != 2 {
		return fmt.Errorf("Subchapter is expected to be of the form <Roman Numeral>-<Letter>")
	}
	return nil
}

type SubchapterList []SubchapterArg
type PartList []string

func (sl *SubchapterList) UnmarshalText(data []byte) error {
	subchapters := strings.Split(string(data), ",")
	*sl = make([]SubchapterArg, 0, len(subchapters))
	for _, subchapter := range subchapters {
		var sc SubchapterArg
		sc.Set(subchapter)
		*sl = append(*sl, sc)
	}
	return nil
}

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

type TitleConfig struct {
	Title int `json:"title"`
	Subchapters SubchapterList `json:"subchapters"`
	Parts PartList `json:"parts"`
}

type ParserConfig struct {
	Workers int `json:"workers"`
	Attempts int `json:"attempts"`
	LogLevel string `json:"loglevel"`
	UploadSupplemental bool `json:"upload_supplemental_locations"`
	LogParseErrors bool `json:"log_parse_errors"`
	SkipVersions bool `json:"skip_versions"`
	Titles []*TitleConfig `json:"titles"`
}

func RetrieveConfig() (*ParserConfig, error) {
	configURL, err := url.Parse(BaseURL)
	if err != nil {
		return nil, fmt.Errorf("%s is not a valid URL! Please correctly set the EREGS_API_URL environment variable.", BaseURL)
	}
	configURL.Path = path.Join(configURL.Path, "/parser_config")

	log.Debug("[config] Retrieving parser configuration from ", configURL.String())

	ctx, cancel := context.WithTimeout(context.Background(), 30 * time.Second)
	defer cancel()
	body, err := network.Fetch(ctx, configURL, true)
	if err != nil {
		return nil, err
	}

	var config ParserConfig
	d := json.NewDecoder(body)
	if err := d.Decode(&config); err != nil {
		return nil, fmt.Errorf("Unable to decode configuration from response body: %+v", err)
	}

	return &config, nil
}
