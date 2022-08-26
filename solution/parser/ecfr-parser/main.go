package main

import (
	"container/list"
	"context"
	"encoding/json"
	"encoding/xml"
	"fmt"
	"net/http"
	"os"
	"sort"
	"strings"
	"sync"
	"time"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/eregs"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/parsexml"

	"github.com/aws/aws-lambda-go/lambda"

	log "github.com/sirupsen/logrus"
)

// TIMELIMIT is the total amount of time the process has to run before being cancelled and marked as a failure
const TIMELIMIT = 5000 * time.Second

// DefaultBaseURL is the default eRegs API URL to use if none is specified
var DefaultBaseURL = "http://localhost:8000/v2/"

// Functions for easy testing via patching
var (
	ParseTitleFunc         = parseTitle
	StartVersionWorkerFunc = startVersionWorker
	HandleVersionFunc      = handleVersion
	SleepFunc              = time.Sleep
)

var config = &eregs.ParserConfig{}

func init() {
	eregs.BaseURL = os.Getenv("EREGS_API_URL")
	if eregs.BaseURL == "" {
		eregs.BaseURL = DefaultBaseURL
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
		log.Warn("[main] '", config.LogLevel, "' is an invalid log level, defaulting to 'warn'.")
		return log.WarnLevel
	}
}

func parseConfig(c *eregs.ParserConfig) {
	parsexml.LogParseErrors = c.LogParseErrors

	if c.Workers < 1 {
		log.Warn("[main] ", c.Workers, " is an invalid number of workers, defaulting to 1.")
		c.Workers = 1
	}

	log.SetLevel(getLogLevel(c.LogLevel))
}

// Only runs if parser is in a Lambda
func lambdaHandler(ctx context.Context) (string, error) {
	err := start()
	return "Operation complete.", err
}

func main() {
	log.Info("[main] eCFR parser starting")
	if os.Getenv("PARSER_ON_LAMBDA") == "true" {
		lambda.Start(lambdaHandler)
	} else if err := start(); err != nil {
		log.Fatal("[main] Parser failed: ", err)
	}
}

func start() error {
	log.Info("[main] Loading configuration...")
	var err error
	config, _, err = eregs.RetrieveConfig()
	if err != nil {
		return fmt.Errorf("failed to retrieve configuration: %+v", err)
	}
	parseConfig(config)

	start := time.Now()
	failed := 0
	processed := 0
	failedTitles := []string{}

	for _, title := range config.Titles {
		if err := ParseTitleFunc(title); err != nil {
			failed++
			log.Error("[main] Failed to parse title ", title.Title, ": ", err)
			failedTitles = append(failedTitles, fmt.Sprintf("%d", title.Title))
		} else {
			processed++
		}
	}

	log.Info("[main] Successfully parsed ", processed, "/", len(config.Titles), " titles.")
	if failed > 0 {
		return fmt.Errorf("the following titles failed to parse: %s", strings.Join(failedTitles, ", "))
	}
	log.Debug("[main] Finished parsing ", len(config.Titles), " titles in ", time.Since(start))
	return nil
}

func parseTitle(title *eregs.TitleConfig) error {
	ctx, cancel := context.WithTimeout(context.Background(), TIMELIMIT)
	defer cancel()

	log.Debug("[main] Fetching table of contents for title ", title.Title, "...")
	toc, code, err := eregs.GetTitle(ctx, title.Title)
	if err != nil {
		if code != http.StatusNotFound {
			return fmt.Errorf("failed to retrieve existing table of contents for title %d. Error code is %d, so processing of this title will be skipped. Error: %+v", title.Title, code, err)
		}
		log.Info("[main] Received 404 while trying to retrieve existing table of contents for title ", title.Title, ", defaulting to an empty one.")
	}
	if !config.SkipVersions {
		toc.Contents = &ecfr.Structure{}
	}
	title.Contents = toc

	start := time.Now()

	result := eregs.ParserResult{
		Start:   start.Format(time.RFC3339),
		Title:   title.Title,
		Parts:   strings.Join(title.Parts[:], ","),
		Workers: config.Workers,
	}
	defer eregs.PostParserResult(ctx, &result)

	log.Info("[main] Fetching list of existing versions for title ", title.Title, "...")
	existingVersions, _, err := eregs.GetExistingParts(ctx, title.Title)
	if err != nil {
		log.Warn("[main] Failed to retrieve existing versions, processing all versions: ", err)
	}

	log.Info("[main] Fetching parts list for title ", title.Title, "...")
	var parts []string
	for _, subchapter := range title.Subchapters {
		log.Debug("[main] Fetching title ", title.Title, " subchapter ", subchapter, " parts list...")
		result.Subchapters = result.Subchapters + subchapter.String()
		var err error
		var subchapterParts []string
		subchapterParts, err = ecfr.ExtractSubchapterParts(ctx, title.Title, &ecfr.SubchapterOption{subchapter[0], subchapter[1]})
		if err != nil {
			return err
		}
		parts = append(parts, subchapterParts...)
	}
	parts = append(parts, title.Parts...)

	if len(parts) < 1 {
		return fmt.Errorf("some number of parts must be specified")
	}

	log.Debug("[main] Extracting versions for title ", title.Title, "...")
	versions, err := ecfr.ExtractVersions(ctx, title.Title)
	if err != nil {
		return err
	}

	// Create list of versions to process
	partList := list.New()
	skippedVersions := 0
	numVersions := 0
	for _, part := range parts {
		versionList := list.New()

		// sort versions ascending
		keys := make([]string, 0, len(versions[part]))
		for k := range versions[part] {
			keys = append(keys, k)
		}
		sort.Strings(keys)

		for _, date := range keys {
			// If we have this part already, skip it
			if config.SkipVersions && contains(existingVersions[date], part) {
				log.Trace("[main] Skipping title ", title.Title, " part ", part, " version ", date)
				skippedVersions++
				continue
			}

			version := &eregs.Part{
				Title:          title.Title,
				Name:           part,
				Date:           date,
				Structure:      &ecfr.Structure{},
				Document:       &parsexml.Part{},
				Processed:      false,
				UploadContents: false,
			}

			versionList.PushBack(version)
			numVersions++
		}

		if versionList.Len() > 0 {
			versionList.Back().Value.(*eregs.Part).UploadContents = true
		}

		partList.PushBack(versionList)
	}

	if skippedVersions > 0 {
		log.Info("[main] Skipped ", skippedVersions, " versions of title ", title.Title, " because they were parsed previously")
		result.SkippedVersions = skippedVersions
	}
	result.TotalVersions = numVersions

	// Spawn worker threads that parse versions in the queue
	// Then wait for worker threads to quit
	log.Info("[main] Fetching and processing ", numVersions, " versions using ", config.Workers, " workers...")
	ch := make(chan *list.List)
	var wg sync.WaitGroup
	for worker := 1; worker < config.Workers+1; worker++ {
		wg.Add(1)
		go StartVersionWorkerFunc(ctx, worker, ch, &wg)
	}

	for versionList := partList.Front(); versionList != nil; versionList = versionList.Next() {
		ch <- versionList.Value.(*list.List)
	}

	log.Debug("[main] Waiting until all versions are finished processing")
	close(ch)
	wg.Wait()

	failed := []string{}
	processed := 0

	for versionListElement := partList.Front(); versionListElement != nil; versionListElement = versionListElement.Next() {
		versionList := versionListElement.Value.(*list.List)
		for versionElement := versionList.Front(); versionElement != nil; versionElement = versionElement.Next() {
			version := versionElement.Value.(*eregs.Part)
			if version.Processed {
				processed++
				if version.UploadContents {
					log.Debug("[main] Adding structure of part ", version.Name, " to Title ", title.Title, "'s table of contents")
					title.Contents.AddPart(version.Structure, version.Name)
					title.Contents.Modified = true
				}
			} else {
				failed = append(failed, fmt.Sprintf("%s ver. %s", version.Name, version.Date))
			}
		}
	}

	log.Info("[main] Successfully processed ", processed, "/", numVersions, " versions of title ", title.Title, " in ", time.Since(start))
	if len(failed) > 0 {
		return fmt.Errorf("the following versions failed to process: %s", strings.Join(failed, ", "))
	}
	return nil
}

func startVersionWorker(ctx context.Context, thread int, ch chan *list.List, wg *sync.WaitGroup) {
	processingAttempts := 0
	processedParts := 0
	processedVersions := 0

	for versionList := range ch {
		processedParts++
		for versionElement := versionList.Front(); versionElement != nil; versionElement = versionElement.Next() {
			processingAttempts++
			version := versionElement.Value.(*eregs.Part)
			log.Debug("[worker ", thread, "] Processing part ", version.Name, " version ", version.Date)
			err := HandleVersionFunc(ctx, thread, version)
			if err == nil {
				version.Processed = true
				processedVersions++
			} else {
				log.Error("[worker ", thread, "] Error processing part ", version.Name, " version ", version.Date, ": ", err)
			}
			SleepFunc(1 * time.Second)
		}
	}

	log.Debug("[worker ", thread, "] Worker successfully processed ", processedVersions, "/", processingAttempts, " versions of ", processedParts, " parts.")
	wg.Done()
}

func handleVersion(ctx context.Context, thread int, version *eregs.Part) error {
	start := time.Now()

	log.Debug("[worker ", thread, "] Fetching structure for part ", version.Name, " version ", version.Date)
	sbody, _, err := ecfr.FetchStructure(ctx, version.Title, &ecfr.PartOption{version.Name})

	if err != nil {
		return err
	}

	log.Trace("[worker ", thread, "] Decoding structure for part ", version.Name, " version ", version.Date)
	sd := json.NewDecoder(sbody)
	if err := sd.Decode(version.Structure); err != nil {
		return err
	}

	log.Debug("[worker ", thread, "] Fetching full document for part ", version.Name, " version ", version.Date)
	body, _, err := ecfr.FetchFull(ctx, version.Date, version.Title, &ecfr.PartOption{version.Name})
	if err != nil {
		return err
	}

	log.Trace("[worker ", thread, "] Decoding full structure for part ", version.Name, " version ", version.Date)
	d := xml.NewDecoder(body)
	if err := d.Decode(version.Document); err != nil {
		return err
	}

	log.Debug("[worker ", thread, "] Running post process on structure for part ", version.Name, " version ", version.Date)
	version.Document.PostProcess()

	log.Trace("[worker ", thread, "] Determining depth of part ", version.Name, " version ", version.Date)
	version.Depth = ecfr.DeterminePartDepth(version.Structure, version.Name)
	if version.Depth == -1 {
		return fmt.Errorf("unable to determine depth of part in structure")
	}

	log.Trace("[worker ", thread, "] Computing section parents for part ", version.Name, " version ", version.Date)
	ecfr.DetermineParents(version.Structure)

	log.Debug("[worker ", thread, "] Posting part ", version.Name, " version ", version.Date, " to eRegs")
	if _, err := eregs.PostPart(ctx, version); err != nil {
		return err
	}

	if config.UploadSupplemental {
		log.Debug("[worker ", thread, "] Extracting supplemental content structure for part ", version.Name, " version ", version.Date)
		supplementalPart, err := ecfr.ExtractStructure(*version.Structure)
		if err != nil {
			return err
		}

		log.Debug("[worker ", thread, "] Posting supplemental content structure for part ", version.Name, " version ", version.Date, " to eRegs")
		if _, err := eregs.PostSupplementalPart(ctx, supplementalPart); err != nil {
			return err
		}
	}

	log.Debug("[worker ", thread, "] Successfully processed part ", version.Name, " version ", version.Date, " in ", time.Since(start))
	return nil
}

func contains(s []string, str string) bool {
	for _, v := range s {
		if v == str {
			return true
		}
	}

	return false
}
