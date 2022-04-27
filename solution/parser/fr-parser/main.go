package main

import (
	"time"
	"context"
	"os"
	"fmt"
	"strings"

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
	url := os.Getenv("EREGS_API_URL")
	if url == "" {
		url = DefaultBaseURL
	}

	v3url := url
	if strings.HasSuffix(v3url, "v2/") {
		v3url = v3url[0:len(v3url)-3] + "v3/" // very bad!
	}

	ecfrEregs.BaseURL = url
	eregs.BaseURL = v3url
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

var retrieveConfigFunc = ecfrEregs.RetrieveConfig
var getLogLevelFunc = getLogLevel

func loadConfig() (*ecfrEregs.ParserConfig, error) {
	log.Info("[main] Loading configuration...")
	config, _, err := retrieveConfigFunc()
	if err != nil {
		return nil, err
	}

	// parse config here
	log.SetLevel(getLogLevel(config.LogLevel))

	return config, nil
}

var extractSubchapterPartsFunc = ecfr.ExtractSubchapterParts

func getPartsList(ctx context.Context, t *ecfrEregs.TitleConfig) []string {
	today := time.Now()
	var parts []string
	for _, subchapter := range t.Subchapters {
		subchapterParts, err := extractSubchapterPartsFunc(ctx, today, t.Title, &ecfr.SubchapterOption{subchapter[0], subchapter[1]})
		if err != nil {
			log.Error("[main] Failed to retrieve parts for title ", t.Title, " subchapter ", subchapter, ". Skipping.")
			continue
		}
		parts = append(parts, subchapterParts...)
	}
	parts = append(parts, t.Parts...)
	return parts
}

var loadConfigFunc = loadConfig
var getPartsListFunc = getPartsList
var processPartFunc = processPart

func start() error {
	ctx, cancel := context.WithTimeout(context.Background(), TIMELIMIT)
	defer cancel()

	config, err := loadConfigFunc()
	if err != nil {
		return fmt.Errorf("Failed to retrieve configuration: %+v", err)
	}

	for _, title := range config.Titles {
		log.Info("[main] Retrieving content for title ", title.Title)
		parts := getPartsListFunc(ctx, title)
		for _, part := range parts {
			if err := processPartFunc(ctx, title.Title, part); err != nil {
				log.Error("[main] Failed to process title ", title.Title, " part ", part, ": ", err)
			}
		}
	}

	return nil
}

var fetchContentFunc = fedreg.FetchContent
var processDocumentFunc = processDocument

func processPart(ctx context.Context, title int, part string) error {
	log.Debug("[main] Retrieving list of content for title ", title, " part ", part)
	content, err := fetchContentFunc(ctx, title, part)
	if err != nil {
		return fmt.Errorf("Fetch content failed: %+v", err)
	}

	log.Debug("[main] Processing content for title ", title, " part ", part)
	for _, c := range content {
		if err := processDocumentFunc(ctx, title, part, c); err != nil {
			log.Error("[main] Failed to process title ", title, " part ", part, " doc ID ", c.DocumentNumber, ": ", err)
		}
	}

	return nil
}

var fetchSectionsFunc = fedreg.FetchSections
var sendDocumentFunc = eregs.SendDocument

func processDocument(ctx context.Context, title int, part string, content *fedreg.FRDoc) error {
	doc := &eregs.FRDoc{
		Name: content.Name,
		Description: content.Description,
		Category: content.Category,
		URL: content.URL,
		Date: content.Date,
		DocketNumber: content.DocketNumber,
		DocumentNumber: content.DocumentNumber,
	}

	if content.FullTextURL != "" {
		log.Trace("[main] Retrieving list of associated sections for title ", title, " part ", part, " doc ID ", content.DocumentNumber)
		sections, err := fetchSectionsFunc(ctx, content.FullTextURL)
		if err != nil {
			log.Error("[main] Failed to fetch list of sections for FR doc ", content.DocumentNumber, ": ", err)
		} else {
			doc.Locations = eregs.CreateSections(fmt.Sprintf("%d", title), sections)
		}
	}

	log.Trace("[main] Sending title ", title, " part ", part, " doc ID ", content.DocumentNumber, " to eRegs")
	if err := sendDocumentFunc(ctx, doc); err != nil {
		return fmt.Errorf("Failed to send document to eRegs: %+v", err)
	}

	return nil
}
