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

	log "github.com/sirupsen/logrus"
)

type SubchapterList []string
type PartList []int

func (sl *SubchapterList) UnmarshalText(data []byte) error {
	*sl = strings.Split(string(data), ",")
	return nil
}

func (pl *PartList) UnmarshalText(data []byte) error {
	tmp := strings.Split(string(data), ",")
	*pl = make([]int, 0, len(tmp))
	for _, raw := range tmp {
		v, err := strconv.Atoi(raw)
		if err != nil {
			log.Error("[config] ", raw, " is not a valid part, skipping.")
			continue
		}
		*pl = append(*pl, v)
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
	q := configURL.Query()
	q.Add("json_errors", "true")
	configURL.RawQuery = q.Encode()

	log.Debug("[config] Retrieving parser configuration from ", configURL.String())

	ctx, cancel := context.WithTimeout(context.Background(), 30 * time.Second)
	defer cancel()
	body, err := fetch(ctx, configURL)
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
