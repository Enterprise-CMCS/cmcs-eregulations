package main

import (
	"time"
	"context"
	"os"

	"github.com/cmsgov/cmcs-eregulations/fr-parser/eregs"

	ecfrEregs "github.com/cmsgov/cmcs-eregulations/ecfr-parser/eregs"

	"github.com/aws/aws-lambda-go/lambda"

	log "github.com/sirupsen/logrus"
)

// TIMELIMIT is the total amount of time the process has to run before being cancelled
const TIMELIMIT = 5000 * time.Second

// DefaultBaseURL is the default eRegs API URL to use if none is specified
var DefaultBaseURL = "http://localhost:8000/v2/"

func init() {
	eregs.BaseURL = os.Getenv("EREGS_API_URL")
	if eregs.BaseURL == "" {
		eregs.BaseURL = DefaultBaseURL
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
		log.Warn("[main] \"", config.LogLevel, "\" is an invalid log level, defaulting to \"warn\".")
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
	log.SetLevel(getLogLevel(c.LogLevel))

	return config, nil
}

func getPartsList(c *ecfrEregs.ParserConfig) map[int][]string {
	partMap := make(map[int][]string)
	today := time.Now()
	for _, title := range c.Titles {
		var parts []string
		for _, subchapter := range title.Subchapters {
			log.Debug("[main] Fetching title ", title.Title, " subchapter ", subchapter, " parts list...")
			subchapterParts, err := ecfr.ExtractSubchapterParts(ctx, today, title.Title, &ecfr.SubchapterOption{subchapter[0], subchapter[1]})
			if err != nil {
				log.Error("[main] Failed to retrieve parts for title ", title.Title, " subchapter ", subchapter, ". Skipping.")
				continue
			}
			parts = append(parts, subchapterParts...)
		}
		parts = append(parts, title.Parts...)
		partMap[title.Title] = parts
	}
	return partsMap
}

func start() error {
	config, err := loadConfig()
	if err != nil {
		return fmt.Errorf("Failed to retrieve configuration: %+v", err)
	}

	partMap, err := getPartsList(config)
	if err != nil {
		return fmt.Errorf("Failed to compile list of parts: %+v", err)
	}
}
