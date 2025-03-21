package main

import (
	"context"
	"fmt"
	"os"
	"time"
	"encoding/json"

	"github.com/cmsgov/cmcs-eregulations/lib/eregs"
	"github.com/cmsgov/cmcs-eregulations/lib/fedreg"

	"github.com/aws/aws-lambda-go/lambda"

	log "github.com/sirupsen/logrus"
)

// TIMELIMIT is the total amount of time the process has to run before being cancelled
const TIMELIMIT = 5000 * time.Second

type lambdaEvent struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

// Only runs if parser is in a Lambda
func lambdaHandler(ctx context.Context, event json.RawMessage) (string, error) {
	// Set EREGS_USERNAME and EREGS_PASSWORD environment variables
	// This is only for a single invocation and not stored anywhere
	var e lambdaEvent
	if err := json.Unmarshal(event, &e); err != nil {
		return "", fmt.Errorf("failed to unmarshal event: %s", err)
	}
	eregs.PostAuth.Username = e.Username
	eregs.PostAuth.Password = e.Password
	
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

var retrieveConfigFunc = eregs.RetrieveConfig

//lint:ignore U1000 This is required for the tests to work, even if it is not used in this file.
var getLogLevelFunc = eregs.GetLogLevel

func loadConfig() (*eregs.ParserConfig, error) {
	log.Info("[main] Loading configuration...")
	config, _, err := retrieveConfigFunc()
	if err != nil {
		return nil, err
	}

	// parse config here
	log.SetLevel(getLogLevelFunc(config.LogLevel))

	return config, nil
}

var loadConfigFunc = loadConfig
var processPartFunc = processPart
var fetchDocumentListFunc = eregs.FetchDocumentList
var processPartsListFunc = eregs.ProcessPartsList

func start() error {
	ctx, cancel := context.WithTimeout(context.Background(), TIMELIMIT)
	defer cancel()

	config, err := loadConfigFunc()
	if err != nil {
		return fmt.Errorf("failed to retrieve configuration: %+v", err)
	}

	log.Debug("[main] retrieving list of processed content")
	existingDocsList, err := fetchDocumentListFunc(ctx)
	if err != nil {
		return fmt.Errorf("failed to retrieve list of already processed documents: %+v", err)
	}
	existingDocs := make(map[string]bool)
	for _, i := range existingDocsList {
		existingDocs[i] = true
	}

	titles := make(map[string]struct{})
	titleConfig := make(map[int][]*eregs.PartConfig)
	for _, part := range config.Parts {
		if part.UploadFRDocs {
			titles[fmt.Sprintf("%d", part.Title)] = struct{}{}
			titleConfig[part.Title] = append(titleConfig[part.Title], part)
		}
	}

	for title, rawParts := range titleConfig {
		log.Info("[main] retrieving content for title ", title)
		parts, err := processPartsListFunc(ctx, title, rawParts)
		if err != nil {
			return fmt.Errorf("failed to process parts list: %+v", err)
		}
		for _, part := range parts {
			if err := processPartFunc(ctx, title, part.Value, existingDocs, config.SkipFRDocuments, titles); err != nil {
				log.Error("[main] failed to process title ", title, " part ", part.Value, ": ", err)
			}
		}
	}

	return nil
}

var fetchContentFunc = fedreg.FetchContent
var processDocumentFunc = processDocument

func processPart(ctx context.Context, title int, part string, existingDocs map[string]bool, skip bool, titles map[string]struct{}) error {
	log.Debug("[main] retrieving list of content for title ", title, " part ", part)
	contentList, err := fetchContentFunc(ctx, title, part)
	if err != nil {
		return fmt.Errorf("fetch content failed: %+v", err)
	}

	var content []*fedreg.FRDoc
	if skip {
		removed := 0
		for _, c := range contentList {
			if existingDocs[c.DocumentNumber] {
				removed++
			} else {
				content = append(content, c)
			}
		}
		log.Debug("[main] Skipped ", removed, "/", len(contentList), " documents for title ", title, " part ", part)
	} else {
		content = contentList
	}

	log.Debug("[main] Processing content for title ", title, " part ", part)
	for _, c := range content {
		if err := processDocumentFunc(ctx, title, part, c, titles); err != nil {
			log.Error("[main] failed to process title ", title, " part ", part, " doc ID ", c.DocumentNumber, ": ", err)
		}
	}

	return nil
}

var fetchSectionsFunc = fedreg.FetchSections
var sendDocumentFunc = eregs.SendDocument

func processDocument(ctx context.Context, title int, part string, content *fedreg.FRDoc, titles map[string]struct{}) error {
	doc := &eregs.FRDoc{
		Name:           content.Name,
		Description:    content.Description,
		DocType:        content.Category,
		URL:            content.URL,
		Date:           content.Date,
		DocketNumbers:  content.DocketNumbers,
		DocumentNumber: content.DocumentNumber,
		RawTextURL:     content.RawTextURL,
	}

	if content.FullTextURL != "" {
		log.Trace("[main] retrieving list of associated sections for title ", title, " part ", part, " doc ID ", content.DocumentNumber)
		sections, sectionRanges, partMap, err := fetchSectionsFunc(ctx, content.FullTextURL, titles)
		if err != nil {
			log.Error("[main] failed to fetch list of sections for FR doc ", sectionRanges, " ", content.DocumentNumber, ": ", err)
		} else {
			doc.Sections = eregs.CreateSections(sections, partMap)
			doc.SectionRanges = eregs.CreateSectionRanges(sectionRanges, partMap)
		}
	} else {
		log.Warn("[main] no list of sections available for FR doc ", content.DocumentNumber)
	}

	log.Trace("[main] sending title ", title, " part ", part, " doc ID ", content.DocumentNumber, " to eRegs")
	if err := sendDocumentFunc(ctx, doc); err != nil {
		return fmt.Errorf("failed to send document to eRegs: %+v", err)
	}

	return nil
}
