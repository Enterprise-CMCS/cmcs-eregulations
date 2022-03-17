package main

import (
	"container/list"
	"context"
	"encoding/json"
	"encoding/xml"
	"fmt"
	"os"
	"sync"
	"time"
	"sort"

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
	ParseTitleFunc = parseTitle
	StartHandlePartVersionWorkerFunc = startHandlePartVersionWorker
	HandlePartVersionFunc = handlePartVersion
	SleepFunc = time.Sleep
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
		log.Warn("[main] \"", config.LogLevel, "\" is an invalid log level, defaulting to \"warn\".")
		return log.WarnLevel
	}
}

func parseConfig(c *eregs.ParserConfig) {
	parsexml.LogParseErrors = c.LogParseErrors

	if c.Workers < 1 {
		log.Warn("[main] ", c.Workers, " is an invalid number of workers, defaulting to 1.")
		c.Workers = 1
	}

	if c.Attempts < 1 {
		log.Warn("[main] ", c.Attempts, " is an invalid number of attempts, defaulting to 1.")
		c.Attempts = 1
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
	config, err = eregs.RetrieveConfig()
	if err != nil {
		return fmt.Errorf("Failed to retrieve configuration: %+v", err)
	}
	parseConfig(config)

	queue := list.New()
	for _, title := range config.Titles {
		queue.PushBack(title)
	}

	start := time.Now()

	var failed bool
	for i := 0; i < config.Attempts; i++ {
		originalLength := queue.Len()
		processed := 0
		failed = false
		log.Info("[main] Begin parsing ", originalLength, " titles.")

		var next *list.Element
		for titleElement := queue.Front(); titleElement != nil; titleElement = next {
			next = titleElement.Next()
			title := titleElement.Value.(*eregs.TitleConfig)

			log.Info("[main] Parsing title ", title.Title, "...")
			if retry, err := ParseTitleFunc(title); err == nil {
				queue.Remove(titleElement)
				processed++
			} else if !retry {
				log.Error("[main] Failed to parse title ", title.Title, ". Will not retry. Error: ", err)
				queue.Remove(titleElement)
				failed = true
			} else if i >= config.Attempts-1 {
				log.Error("[main] Failed to parse title ", title.Title, " ", config.Attempts, " times. Error: ", err)
				queue.Remove(titleElement)
				failed = true
			} else {
				log.Error("[main] Failed to parse title ", title.Title, ". Error: ", err)
				failed = true
			}
		}

		log.Info("[main] Successfully parsed ", processed, "/", originalLength, " titles.")

		if queue.Len() < 1 {
			break
		}

		if failed && i < config.Attempts {
			log.Error("[main] Some titles failed to parse. Will retry ", config.Attempts-i-1, " more times.")
		} else if !failed {
			break
		}
	}

	if failed {
		return fmt.Errorf("Some titles failed to process after %d attempts", config.Attempts)
	}
	log.Debug("[main] Finished parsing ", len(config.Titles), " titles in ", time.Since(start))
	return nil
}

func parseTitle(title *eregs.TitleConfig) (bool, error) {
	ctx, cancel := context.WithTimeout(context.Background(), TIMELIMIT)
	defer cancel()

	start := time.Now()
	today := time.Now()

	log.Info("[main] Fetching list of existing versions for title ", title.Title, "...")
	existingVersions, err := eregs.GetExistingParts(ctx, title.Title)
	if err != nil {
		log.Warn("Failed to retrieve existing versions, processing all versions: ", err)
	}

	log.Info("[main] Fetching table of contents for title ", title.Title, "...")
	toc, err := eregs.GetTitle(ctx, title.Title)
	if err != nil {
		// TODO: check error code. If it isn't 404, there might be a worse problem to solve!
		log.Warn("Failed to retrieve existing table of contents for title ", title.Title, ", defaulting to an empty one: ", err)
	}

	log.Info("[main] Fetching parts list for title ", title.Title, "...")
	var parts []string
	for _, subchapter := range title.Subchapters {
		log.Debug("[main] Fetching title ", title.Title, " subchapter ", subchapter, " parts list...")
		var err error
		parts, err = ecfr.ExtractSubchapterParts(ctx, today, title.Title, &ecfr.SubchapterOption{subchapter[0], subchapter[1]})
		if err != nil {
			return true, err
		}
	}
	parts = append(parts, title.Parts...)

	if len(parts) < 1 {
		return false, fmt.Errorf("Some number of parts must be specified")
	}

	log.Debug("[main] Extracting versions for title ", title.Title, "...")
	versions, err := ecfr.ExtractVersions(ctx, title.Title)
	if err != nil {
		return true, err
	}

	// Create initial list of versions to process
	partList := list.New()
	skippedVersions := 0
	originalLength := 0
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
				Title:     		title.Title,
				Name:      		part,
				Date:      		date,
				Structure: 		&ecfr.Structure{},
				Document:  		&parsexml.Part{},
				Processed: 	    false,
				UploadContents: false,
			}

			versionList.PushBack(version)
			originalLength++
		}

		if versionList.Len() > 0 {
			versionList.Back().Value.(*eregs.Part).UploadContents = true
		}

		partList.PushBack(versionList)
	}

	if skippedVersions > 0 {
		log.Info("[main] Skipped ", skippedVersions, " versions of title ", title.Title, " because they were parsed previously")
	}

	// Begin processing loop
	// Spawns `workers` threads that parse versions in the queue
	// If parsing fails, version kept in queue for next run (if any remain)

	for i := 0; i < config.Attempts; i++ {
		log.Info("[main] Fetching and processing ", originalLength, " versions using ", config.Workers, " workers...")

		ch := make(chan *list.List)
		var wg sync.WaitGroup
		for worker := 1; worker < config.Workers+1; worker++ {
			wg.Add(1)
			go StartHandlePartVersionWorkerFunc(ctx, worker, ch, &wg, today)
		}

		for versionList := partList.Front(); versionList != nil; versionList = versionList.Next() {
			ch <- versionList.Value.(*list.List)
		}

		log.Debug("[main] Waiting until all versions are finished processing")
		close(ch)
		wg.Wait()

		log.Trace("[main] Removing successfully processed versions from the queue")
		currentLength := 0
		for versionListElement := partList.Front(); versionListElement != nil; versionListElement = versionListElement.Next() {
			versionList := versionListElement.Value.(*list.List)
			var next *list.Element
			for versionElement := versionList.Front(); versionElement != nil; versionElement = next {
				next = versionElement.Next()
				version := versionElement.Value.(*eregs.Part)
				if version.Processed {
					if version.UploadContents {
						log.Debug("[main] Adding structure of part ", version.Name, " to Title ", title.Title, "'s table of contents")
						toc.AddPart(version.Structure, version.Name)
					}
					versionList.Remove(versionElement)
				} else {
					currentLength++
				}
			}
		}

		log.Info("[main] Successfully processed ", originalLength-currentLength, "/", originalLength, " versions")
		originalLength = currentLength

		if currentLength == 0 {
			break
		} else if i >= config.Attempts-1 {
			return false, fmt.Errorf("Some parts still failed to process after %d attempts", config.Attempts)
		} else {
			log.Warn("[main] Some parts failed to process. Retrying ", config.Attempts-i-1, " more times.")
			SleepFunc(3 * time.Second)
		}
	}

	log.Info("[main] Uploading table of contents to eRegs...")
	if err := eregs.SendTitle(ctx, &toc); err != nil {
		log.Error("[main] Failed to upload table of contents for Title ", title.Title, ": ", err)
	}
	log.Info("[main] All parts of title ", title.Title, " finished processing in ", time.Since(start), "!")
	return false, nil
}

func startHandlePartVersionWorker(ctx context.Context, thread int, ch chan *list.List, wg *sync.WaitGroup, date time.Time) {
	processingAttempts := 0
	processedParts := 0
	processedVersions := 0

	for versionList := range ch {
		processedParts++
		for versionElement := versionList.Front(); versionElement != nil; versionElement = versionElement.Next() {
			processingAttempts++
			version := versionElement.Value.(*eregs.Part)
			log.Debug("[worker ", thread, "] Processing part ", version.Name, " version ", version.Date)
			err := HandlePartVersionFunc(ctx, thread, date, version)
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

func handlePartVersion(ctx context.Context, thread int, date time.Time, version *eregs.Part) error {
	start := time.Now()

	log.Debug("[worker ", thread, "] Fetching structure for part ", version.Name, " version ", version.Date)
	sbody, err := ecfr.FetchStructure(ctx, date.Format("2006-01-02"), version.Title, &ecfr.PartOption{version.Name})

	if err != nil {
		return err
	}

	log.Trace("[worker ", thread, "] Decoding structure for part ", version.Name, " version ", version.Date)
	sd := json.NewDecoder(sbody)
	if err := sd.Decode(version.Structure); err != nil {
		return err
	}

	log.Debug("[worker ", thread, "] Fetching full document for part ", version.Name, " version ", version.Date)
	body, err := ecfr.FetchFull(ctx, version.Date, version.Title, &ecfr.PartOption{version.Name})
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

	log.Debug("[worker ", thread, "] Posting part ", version.Name, " version ", version.Date, " to eRegs")
	if err := eregs.PostPart(ctx, version); err != nil {
		return err
	}

	if config.UploadSupplemental {
		log.Debug("[worker ", thread, "] Extracting supplemental content structure for part ", version.Name, " version ", version.Date)
		supplementalPart, err := ecfr.ExtractStructure(*version.Structure)
		if err != nil {
			return err
		}

		log.Debug("[worker ", thread, "] Posting supplemental content structure for part ", version.Name, " version ", version.Date, " to eRegs")
		if err := eregs.PostSupplementalPart(ctx, supplementalPart); err != nil {
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
