package main

import (
	"time"
	"context"
	"os"
	"fmt"

	"github.com/cmsgov/cmcs-eregulations/fr-parser/eregs"
	"github.com/cmsgov/cmcs-eregulations/fr-parser/fedreg"

	ecfrEregs "github.com/cmsgov/cmcs-eregulations/ecfr-parser/eregs"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"

	"github.com/aws/aws-lambda-go/lambda"

	log "github.com/sirupsen/logrus"
)

// TIMELIMIT is the total amount of time the process has to run before being cancelled
const TIMELIMIT = 5000 * time.Second

// DefaultBaseURL is the default eRegs API URL to use if none is specified
var DefaultBaseURL = "http://localhost:8000/v2/"

func init() {
	eregs.BaseURL = os.Getenv("EREGS_API_URL")
	ecfrEregs.BaseURL = os.Getenv("EREGS_API_URL")
	if eregs.BaseURL == "" {
		eregs.BaseURL = DefaultBaseURL
		ecfrEregs.BaseURL = DefaultBaseURL
	}
}

func lambdaHandler(ctx context.Context) (string, error) {
	err := start()
	return "Operation complete.", err
}

func main() {
	log.Info("[main] Federal Register parser starting")
	if os.Getenv("PARSER_ON_LAMBDA") == "true" {
		lambda.Start(lambdaHandler)
	} else if err := start(); err != nil {
		log.Fatal("[main] Parser failed: ", err)
	}
}

func getLogLevel(l string) log.Level {
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
		log.Warn("[main] \"", l, "\" is an invalid log level, defaulting to \"warn\".")
		return log.WarnLevel
	}
}

func loadConfig() (*ecfrEregs.ParserConfig, error) {
	log.Info("[main] Loading configuration...")
	config, _, err := ecfrEregs.RetrieveConfig()
	if err != nil {
		return nil, err
	}

	// parse config here
	log.SetLevel(getLogLevel(config.LogLevel))

	return config, nil
}

func getPartsList(ctx context.Context, t *ecfrEregs.TitleConfig) []string {
	today := time.Now()
	var parts []string
	for _, subchapter := range t.Subchapters {
		subchapterParts, err := ecfr.ExtractSubchapterParts(ctx, today, t.Title, &ecfr.SubchapterOption{subchapter[0], subchapter[1]})
		if err != nil {
			log.Error("[main] Failed to retrieve parts for title ", t.Title, " subchapter ", subchapter, ". Skipping.")
			continue
		}
		parts = append(parts, subchapterParts...)
	}
	parts = append(parts, t.Parts...)
	return parts
}

func start() error {
	ctx, cancel := context.WithTimeout(context.Background(), TIMELIMIT)
	defer cancel()

	config, err := loadConfig()
	if err != nil {
		return fmt.Errorf("Failed to retrieve configuration: %+v", err)
	}

	for _, title := range config.Titles {
		log.Debug("[main] Retrieving parts list for title ", title.Title)
		parts := getPartsList(ctx, title)
		for _, part := range parts {
			content, err := fedreg.FetchContent(ctx, title.Title, part)
			if err != nil {
				log.Error("[main] Failed to fetch FR docs for title ", title.Title, " part ", part, ": ", err)
				continue
			}

			for _, c := range content {
				sections, err := fedreg.FetchSections(ctx, c.Date, c.DocumentNumber)
				if err != nil {
					log.Error("[main] Failed to fetch list of sections FR doc ", c.DocumentNumber, ": ", err)
					continue
				}
				c.Sections = sections
			}
		}
	}

	return nil
}
