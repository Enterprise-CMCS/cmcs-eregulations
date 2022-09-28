package main

import (
	"context"
	"fmt"
	"os"
	"time"

	"github.com/cmsgov/cmcs-eregulations/lib/ecfr"
	"github.com/cmsgov/cmcs-eregulations/lib/eregs"
	"github.com/cmsgov/cmcs-eregulations/lib/fedreg"

	"github.com/aws/aws-lambda-go/lambda"

	log "github.com/sirupsen/logrus"
)

// TIMELIMIT is the total amount of time the process has to run before being cancelled
const TIMELIMIT = 5000 * time.Second

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

var extractSubchapterPartsFunc = ecfr.ExtractSubchapterParts

func getPartsList(ctx context.Context, t *eregs.TitleConfig) []string {
	var parts []string
	for _, subchapter := range t.Subchapters {
		subchapterParts, err := extractSubchapterPartsFunc(ctx, t.Title, &ecfr.SubchapterOption{subchapter[0], subchapter[1]})
		if err != nil {
			log.Error("[main] failed to retrieve parts for title ", t.Title, " subchapter ", subchapter, ". Skipping.")
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
var fetchDocumentListFunc = eregs.FetchDocumentList

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
	for _, title := range config.Titles {
		titles[fmt.Sprintf("%d", title.Title)] = struct{}{}
	}

	for _, title := range config.Titles {
		log.Info("[main] retrieving content for title ", title.Title)
		parts := getPartsListFunc(ctx, title)
		for _, part := range parts {
			if err := processPartFunc(ctx, title.Title, part, existingDocs, config.SkipFRDocuments, titles); err != nil {
				log.Error("[main] failed to process title ", title.Title, " part ", part, ": ", err)
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
