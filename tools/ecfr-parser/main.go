package main

import (
	"container/list"
	"context"
	"encoding/json"
	"encoding/xml"
	"flag"
	"fmt"
	"os"
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

// Local arguments set via command-line or environment variable
var (
	attempts        int
	title           int
	subchapter      SubchapterArg
	individualParts PartsArg
	loglevel        string
	workers         int
	skipVersions    bool
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

// PartsArg is an array of type string
type PartsArg []string

func (pa *PartsArg) String() string {
	return strings.Join(*pa, ",")
}

// Set is to validate and set the PartsArg
func (pa *PartsArg) Set(s string) error {
	*pa = strings.Split(s, ",")

	return nil
}

func init() {
	// Parse command-line flags
	flag.Usage = func() {
		fmt.Fprintf(flag.CommandLine.Output(), "eCFR Parser for eRegs\n\n")
		flag.PrintDefaults()
		fmt.Fprintf(flag.CommandLine.Output(), "\nSet USE_ENVIRONMENT_VARS=true to configure with environment variables.\n" +
			"Variables are the same as command line arguments but upper-case with underscores, e.g. 'EREGS_URL' instead of 'eregs-url'.\n\n" +
			"Be sure to also set PARSER_ON_LAMBDA=true if running in AWS Lambda.\n")
	}
	flag.IntVar(&title, "title", -1, "The number of the regulation title to be loaded")
	flag.Var(&subchapter, "subchapter", "A chapter and subchapter separated by a dash, e.g. IV-C")
	flag.Var(&individualParts, "parts", "A comma-separated list of parts to load, e.g. 457,460")
	flag.StringVar(&eregs.BaseURL, "eregs-url", "http://localhost:8080/v2/", "A url specifying where to send eregs parts")
	flag.StringVar(&eregs.SuppContentURL, "eregs-supplemental-url", "", "A url specifying where to send eregs parts")
	flag.IntVar(&workers, "workers", 3, "Number of parts to process simultaneously.")
	flag.IntVar(&attempts, "attempts", 1, "The number of times to attempt regulation loading")
	flag.StringVar(&loglevel, "loglevel", "warn", "Logging severity level. One of: fatal, error, warn, info, debug, trace.")
	flag.BoolVar(&parsexml.LogParseErrors, "log-parse-errors", true, "Output errors encountered while parsing.")
	flag.BoolVar(&skipVersions, "skip-existing-versions", true, "Skip versions of parts that already exist in eRegs.")
	flag.Parse()

	// Retrieve params from environment vars if USE_ENVIRONMENT_VARS is true.
	// Params are named using uppercase with underscores, e.g. 'log-parse-errors' becomes 'LOG_PARSE_ERRORS'.
	if os.Getenv("USE_ENVIRONMENT_VARS") == "true" {
		flag.VisitAll(func(flag *flag.Flag) {
			var envName = strings.Replace(strings.ToUpper(flag.Name), "-", "_", -1)
			var value = os.Getenv(envName)
			if value != "" {
				flag.Value.Set(value)
			}
		})
	}

	if title < 0 {
		log.Fatal("[main] Title flag is required and must be greater than 0.")
	}

	if workers < 1 {
		log.Fatal("[main] Number of worker threads must be at least 1.")
	}

	if attempts < 1 {
		log.Fatal("[main] Number of loading attempts must be at least 1.")
	}

	level := log.WarnLevel
	switch loglevel {
	case "warn":
		level = log.WarnLevel
	case "fatal":
		level = log.FatalLevel
	case "error":
		level = log.ErrorLevel
	case "info":
		level = log.InfoLevel
	case "debug":
		level = log.DebugLevel
	case "trace":
		level = log.TraceLevel
	default:
		log.Warn("[main] \"", loglevel, "\" is an invalid log level, defaulting to \"warn\".")
	}
	log.SetLevel(level)
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
	for i := 0; i < attempts; i++ {
		if retry, err := attemptParsing(); err == nil {
			break
		} else if !retry {
			log.Error("[main] Failed to load regulations. Will not retry.")
			return err
		} else if i >= attempts-1 {
			log.Error("[main] Failed to load regulations ", attempts, " times.")
			return err
		} else {
			log.Error("[main] Failed to load regulations. Retrying ", attempts-i-1, " more times. Error: ", err)
			time.Sleep(3 * time.Second)
		}
	}

	return nil
}

func attemptParsing() (bool, error) {
	ctx, cancel := context.WithTimeout(context.Background(), TIMELIMIT)
	defer cancel()

	start := time.Now()
	defer func() {
		log.Debug("[main] Run time:", time.Since(start))
	}()
	today := time.Now()

	log.Info("[main] Fetching list of existing versions...")
	existingVersions, err := eregs.GetExistingParts(ctx, title)

	log.Info("[main] Fetching parts list...")
	var parts []string
	if subchapter != nil {
		log.Debug("[main] Fetching subchapter ", subchapter, " parts list...")
		var err error
		parts, err = ecfr.ExtractSubchapterParts(ctx, today, title, &ecfr.SubchapterOption{subchapter[0], subchapter[1]})
		if err != nil {
			return true, err
		}
	}
	parts = append(parts, individualParts...)

	if len(parts) < 1 {
		log.Fatal("[main] Some number of parts must be specified")
	}

	log.Debug("[main] Extracting versions...")
	versions, err := ecfr.ExtractVersions(ctx, title)
	if err != nil {
		return true, err
	}

	// Create initial list of versions to process
	partList := list.New()
	skippedVersions := 0
	originalLength := 0
	for _, part := range parts {
		versionList := list.New()

		for date := range versions[part] {
			// If we have this part already, skip it
			if skipVersions && contains(existingVersions[date], part) {
				log.Trace("[main] Skipping part ", part, " version ", date)
				skippedVersions++
				continue
			}

			version := &eregs.Part{
				Title:     title,
				Name:      part,
				Date:      date,
				Structure: &ecfr.Structure{},
				Document:  &parsexml.Part{},
				Processed: false,
			}

			versionList.PushBack(version)
			originalLength++
		}

		partList.PushBack(versionList)
	}

	if skippedVersions > 0 {
		log.Info("[main] Skipped ", skippedVersions, " versions because they were parsed previously")
	}

	// Begin processing loop
	// Spawns `workers` threads that parse versions in the queue
	// If parsing fails, version kept in queue for next run (if any remain)

	for i := 0; i < attempts; i++ {
		log.Info("[main] Fetching and processing ", originalLength, " versions using ", workers, " workers...")

		ch := make(chan *list.List)
		var wg sync.WaitGroup
		for worker := 1; worker < workers+1; worker++ {
			wg.Add(1)
			go startHandlePartVersionWorker(ctx, worker, ch, &wg, today)
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
			for version := versionList.Front(); version != nil; version = next {
				next = version.Next()
				if version.Value.(*eregs.Part).Processed {
					versionList.Remove(version)
				} else {
					currentLength++
				}
			}
		}

		log.Info("[main] Successfully processed ", originalLength-currentLength, "/", originalLength, " versions")
		originalLength = currentLength

		if currentLength == 0 {
			break
		} else if i >= attempts-1 {
			return false, fmt.Errorf("Some parts still failed to process after %d attempts", attempts)
		} else {
			log.Warn("[main] Some parts failed to process. Retrying ", attempts-i-1, " more times.")
			time.Sleep(3 * time.Second)
		}
	}

	log.Info("[main] All parts finished processing!")
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
			err := handlePartVersion(ctx, thread, date, version)
			if err == nil {
				version.Processed = true
				processedVersions++
			} else {
				log.Error("[worker ", thread, "] Error processing part ", version.Name, " version ", version.Date, ": ", err)
			}
			time.Sleep(1 * time.Second)
		}
	}

	log.Trace("[worker ", thread, "] Worker successfully processed ", processedVersions, "/", processingAttempts, " versions of ", processedParts, " parts.")
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
	if err := version.Document.PostProcess(); err != nil {
		return err
	}

	log.Debug("[worker ", thread, "] Posting part ", version.Name, " version ", version.Date, " to eRegs")
	if err := eregs.PostPart(ctx, version); err != nil {
		return err
	}

	if len(eregs.SuppContentURL) > 0 {
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
