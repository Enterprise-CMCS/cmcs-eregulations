package main

import (
	"container/list"
	"context"
	"encoding/json"
	"encoding/xml"
	"fmt"
	"os"
	"sort"
	"strings"
	"sync"
	"time"

	"github.com/cmsgov/cmcs-eregulations/lib/ecfr"
	"github.com/cmsgov/cmcs-eregulations/lib/eregs"
	"github.com/cmsgov/cmcs-eregulations/lib/parsexml"

	"github.com/aws/aws-lambda-go/lambda"

	log "github.com/sirupsen/logrus"
)

// TIMELIMIT is the total amount of time the process has to run before being cancelled and marked as a failure
const TIMELIMIT = 5000 * time.Second

// Functions for easy testing via patching
var (
	ParseTitlesFunc            = parseTitles
	ParseTitleFunc             = parseTitle
	StartVersionWorkerFunc     = startVersionWorker
	HandleVersionFunc          = handleVersion
	SleepFunc                  = time.Sleep
	RetrieveConfigFunc         = eregs.RetrieveConfig
	ProcessPartsListFunc       = eregs.ProcessPartsList
	ExtractSubchapterPartsFunc = ecfr.ExtractSubchapterParts
	GetExistingPartsFunc       = eregs.GetExistingParts
	ExtractVersionsFunc        = ecfr.ExtractVersions
	PostParserResultFunc       = eregs.PostParserResult
)

var config = &eregs.ParserConfig{}

func parseConfig(c *eregs.ParserConfig) {
	parsexml.LogParseErrors = c.LogParseErrors

	if c.Workers < 1 {
		log.Warn("[main] ", c.Workers, " is an invalid number of workers, defaulting to 1.")
		c.Workers = 1
	}

	if c.Retries < 0 {
		log.Warn("[main] ", c.Retries, " is an invalid number of retries, defaulting to 0.")
		c.Retries = 0
	}

	log.SetLevel(eregs.GetLogLevel(c.LogLevel))
}

type lambdaEvent struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

// Only runs if parser is in a Lambda
func lambdaHandler(ctx context.Context, event json.RawMessage) (string, error) {
	// Retrieve eRegs username and password from the lambda event
	// This is only for a single invocation and not stored anywhere
	// The event comes from the parser-launcher lambda only
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
	config, _, err = RetrieveConfigFunc()
	if err != nil {
		return fmt.Errorf("failed to retrieve configuration: %+v", err)
	}
	parseConfig(config)

	for attempt := 0; attempt != config.Retries+1; attempt++ {
		if attempt > 0 {
			config.SkipRegVersions = true //just retry failed versions
		}
		if err := ParseTitlesFunc(); err != nil {
			if attempt == config.Retries {
				return fmt.Errorf("parsing failed after %d attempts: %s", attempt+1, err)
			}
			log.Warn("[main] Parsing failed. Will retry ", config.Retries-attempt, " more times. Error: ", err)
		} else {
			break
		}
	}

	return nil
}

func parseTitles() error {
	start := time.Now()
	failed := 0
	processed := 0
	failedTitles := []string{}

	titles := make(map[int][]*eregs.PartConfig)
	for _, part := range config.Parts {
		titles[part.Title] = append(titles[part.Title], part)
	}

	for title, parts := range titles {
		if err := ParseTitleFunc(title, parts); err != nil {
			failed++
			log.Error("[main] Failed to parse title ", title, ": ", err)
			failedTitles = append(failedTitles, fmt.Sprintf("%d", title))
		} else {
			processed++
		}
	}

	log.Info("[main] Successfully parsed ", processed, "/", len(titles), " titles.")
	if failed > 0 {
		return fmt.Errorf("the following titles failed to parse: %s", strings.Join(failedTitles, ", "))
	}
	log.Debug("[main] Finished parsing ", len(titles), " titles in ", time.Since(start))
	return nil
}

func parseTitle(title int, rawParts []*eregs.PartConfig) error {
	ctx, cancel := context.WithTimeout(context.Background(), TIMELIMIT)
	defer cancel()

	start := time.Now()
	result := eregs.ParserResult{
		Start:   start.Format(time.RFC3339),
		Title:   title,
		Workers: config.Workers,
	}
	defer func() {
		result.End = time.Now().Format(time.RFC3339)
		if _, err := PostParserResultFunc(ctx, &result); err != nil {
			log.Warn("[main] Failed to post parser results for title ", title, ": ", err)
		}
	}()

	log.Info("[main] Fetching list of existing versions for title ", title, "...")
	existingVersions, _, err := GetExistingPartsFunc(ctx, title)
	if err != nil {
		log.Warn("[main] Failed to retrieve existing versions, processing all versions: ", err)
	}

	var partsList []string
	var subchapterList []string
	for _, i := range rawParts {
		if i.Type == "part" {
			partsList = append(partsList, i.Value)
		} else if i.Type == "subchapter" {
			subchapterList = append(subchapterList, i.Value)
		}
	}
	result.Parts = strings.Join(partsList, ", ")
	result.Subchapters = strings.Join(subchapterList, ", ")

	log.Info("[main] Computing parts list for title ", title, "...")
	parts, err := ProcessPartsListFunc(ctx, title, rawParts)
	if err != nil {
		return err
	}

	log.Debug("[main] Extracting versions for title ", title, "...")
	versions, err := ExtractVersionsFunc(ctx, title)
	if err != nil {
		return err
	}

	// Create list of versions to process
	partList := list.New()
	skippedVersions := 0
	numVersions := 0
	for _, part := range parts {
		versionList := list.New()

		// sort versions descending
		keys := make([]string, 0, len(versions[part.Value]))
		for k := range versions[part.Value] {
			keys = append(keys, k)
		}
		//sort.Strings(keys)
		sort.Sort(sort.Reverse(sort.StringSlice(keys)))
		
		// only choose the latest date for processing
		if len(keys) > 0 {
			date := keys[0]

			// if we already have this part, skip it if configured to do so
			if config.SkipRegVersions && contains(existingVersions[date], part.Value) {
				log.Trace("[main] Skipping title ", title, " part ", part.Value, " version ", date)
				skippedVersions++
				continue
			}

			version := &eregs.Part{
				Title:           title,
				Name:            part.Value,
				Date:            date,
				Structure:       &ecfr.Structure{},
				Document:        &parsexml.Part{},
				Sections:        []ecfr.Section{},
				Subparts:        []ecfr.Subpart{},
				Processed:       false,
				UploadRegText:   part.UploadRegText,
				UploadLocations: part.UploadLocations,
			}

			versionList.PushBack(version)
			numVersions++
		}

		if versionList.Len() > 0 && part.UploadLocations {
			versionList.Back().Value.(*eregs.Part).UploadLocations = true
		}

		partList.PushBack(versionList)
	}

	if skippedVersions > 0 {
		log.Info("[main] Skipped ", skippedVersions, " versions of title ", title, " because they were parsed previously")
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

	// Determine how many versions parsed and which failed
	failed := []string{}
	processed := 0
	for versionListElement := partList.Front(); versionListElement != nil; versionListElement = versionListElement.Next() {
		versionList := versionListElement.Value.(*list.List)
		for versionElement := versionList.Front(); versionElement != nil; versionElement = versionElement.Next() {
			version := versionElement.Value.(*eregs.Part)
			if version.Processed {
				processed++
			} else {
				failed = append(failed, fmt.Sprintf("%s ver. %s", version.Name, version.Date))
			}
		}
	}

	log.Info("[main] Successfully processed ", processed, "/", numVersions, " versions of title ", title, " in ", time.Since(start))
	if len(failed) > 0 {
		result.Errors = len(failed)
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

	if version.UploadRegText {
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
	}

	log.Trace("[worker ", thread, "] Determining depth of part ", version.Name, " version ", version.Date)
	version.Depth = ecfr.DeterminePartDepth(version.Structure, version.Name)
	if version.Depth == -1 {
		return fmt.Errorf("unable to determine depth of part in structure")
	}

	log.Trace("[worker ", thread, "] Computing section parents for part ", version.Name, " version ", version.Date)
	ecfr.DetermineParents(version.Structure)

	if config.UploadSupplemental && version.UploadLocations {
		log.Debug("[worker ", thread, "] Extracting supplemental content structure for part ", version.Name, " version ", version.Date)
		sections, subparts, err := ecfr.ExtractStructure(*version.Structure, version.Depth)
		if err != nil {
			return err
		}
		version.Sections = sections
		version.Subparts = subparts
	}

	log.Debug("[worker ", thread, "] Posting part ", version.Name, " version ", version.Date, " to eRegs")
	if _, err := eregs.PutPart(ctx, version); err != nil {
		return err
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
