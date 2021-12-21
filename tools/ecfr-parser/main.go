package main

import (
	"container/list"
	"context"
	"encoding/json"
	"encoding/xml"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"strings"
	"sync"
	"time"
	"net/url"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/eregs"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/parsexml"

	"github.com/aws/aws-lambda-go/lambda"

	log "github.com/sirupsen/logrus"
)

// TIMELIMIT is the total amount of time the process has to run before being cancelled and marked as a failure
const TIMELIMIT = 5000 * time.Second

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

	if os.Getenv("USE_ENVIRONMENT_VARS") == "true" {
		flag.VisitAll(func(flag *flag.Flag) {
			var envName = strings.Replace(strings.ToUpper(flag.Name), "-", "_", -1)
			var value = os.Getenv(envName)
			if value != "" {
				flag.Value.Set(value)
			}
		})
	}

	baseURL, err := url.Parse(eregs.BaseURL)
	if err != nil {
		log.Fatal("[main] eregs-url value \"", eregs.BaseURL, "\" is not a valid URL.")
	}
	q := baseURL.Query()
	q.Add("json_errors", "true")
	baseURL.RawQuery = q.Encode()
	eregs.BaseURL = baseURL.String()

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

func lambdaHandler(ctx context.Context) (string, error) {
	err := start()
	return "Operation complete.", err
}

func main() {
	log.Trace("[main] eCFR parser starting")
	if os.Getenv("PARSER_ON_LAMBDA") == "true" {
		lambda.Start(lambdaHandler)
	} else if err := start(); err != nil {
		log.Fatal("[main] Parser failed: ", err)
	}
}

func start() error {
	for i := 0; i < attempts; i++ {
		log.Trace("Curling the ECFR site")
		out, err := exec.Command("curl", "https://www.ecfr.gov/api/versioner/v1/structure/2021-11-05/title-42.json?chapter=IV&subchapter=C").Output()
		log.Trace("Finished Curling the ECFR site")
		if err != nil {
			log.Trace("cURL failed to fetch eCFR: ", err)
		}
		log.Trace(string(out[:100]))

		log.Trace("Curling Google")
		out, err = exec.Command("curl", "https://www.google.com").Output()
		log.Trace("Finished Curling Google")
		if err != nil {
			log.Trace("cURL failed to fetch Google: ", err)
		}
		log.Trace(string(out[:100]))

		if err = attemptParsing(); err == nil {
			break
		} else if i == attempts-1 {
			log.Error("[main] Failed to load regulations ", attempts, " times.")
			return err
		} else {
			log.Error("[main] Failed to load regulations. Retrying ", attempts-i-1, " more times. Error: ", err)
		}
	}

	return nil
}

func attemptParsing() error {
	ctx, cancel := context.WithTimeout(context.Background(), TIMELIMIT)
	defer cancel()

	start := time.Now()
	defer func() {
		log.Debug("[main] Run time:", time.Since(start))
	}()
	today := time.Now()

	log.Info("[main] Fetching Existing Versions list...")
	existingVersions, err := eregs.GetExistingParts(ctx, title)

	log.Info("[main] Fetching parts list...")
	var parts []string
	if subchapter != nil {
		log.Debug("[main] Fetching subchapter ", subchapter, " parts list...")
		var err error
		parts, err = ecfr.ExtractSubchapterParts(ctx, today, title, &ecfr.SubchapterOption{subchapter[0], subchapter[1]})
		if err != nil {
			return err
		}
	}
	parts = append(parts, individualParts...)

	if len(parts) < 1 {
		log.Fatal("[main] Some number of parts must be specified")
	}

	log.Debug("[main] Extracting versions...")
	versions, err := ecfr.ExtractVersions(ctx, title)
	if err != nil {
		log.Trace("[main] extract Version failed")
		return err
	}

	queue := list.New()
	skippedParts := 0
	for _, part := range parts {
		for date := range versions[part] {
			// If we have this part already, skip it
			if skipVersions && contains(existingVersions[date], part) {
				log.Trace("Skipping part ", part, " for ", date)
				skippedParts++
				continue
			}
			reg := &eregs.Part{
				Title:     title,
				Name:      part,
				Date:      date,
				Structure: &ecfr.Structure{},
				Document:  &parsexml.Part{},
				Processed: false,
			}

			queue.PushBack(reg)
		}
	}

	if skippedParts > 0 {
		log.Info("[main] Skipped ", skippedParts, " parts because they were already imported")
	}

	for i := 0; i < attempts; i++ {
		log.Info("[main] Fetching and processing ", queue.Len(), " parts using ", workers, " workers...")
		ch := make(chan *eregs.Part)
		var wg sync.WaitGroup
		for worker := 1; worker < workers+1; worker++ {
			wg.Add(1)
			go startHandlePartWorker(ctx, worker, ch, &wg, today)
		}

		for reg := queue.Front(); reg != nil; reg = reg.Next() {
			ch <- reg.Value.(*eregs.Part)
		}

		log.Debug("[main] Waiting until all parts are finished processing")
		close(ch)
		wg.Wait()

		log.Trace("[main] Removing successfully processed parts from the queue")
		originalLength := queue.Len()
		var next *list.Element
		for reg := queue.Front(); reg != nil; reg = next {
			next = reg.Next()
			if reg.Value.(*eregs.Part).Processed {
				queue.Remove(reg)
			}
		}
		log.Info("[main] Successfully processed ", originalLength-queue.Len(), "/", originalLength, " parts")

		if queue.Len() == 0 {
			break
		} else if i == attempts-1 {
			log.Fatal("[main] Some parts still failed to process after ", attempts, " attempts.")
		} else {
			log.Warn("[main] Some parts failed to process. Retrying ", attempts-i-1, " more times.")
			time.Sleep(3 * time.Second)
		}
	}

	log.Info("[main] All parts finished processing!")
	return nil
}

func startHandlePartWorker(ctx context.Context, thread int, ch chan *eregs.Part, wg *sync.WaitGroup, date time.Time) {
	for reg := range ch {
		log.Debug("[worker ", thread, "] Processing part ", reg.Name, " version ", reg.Date)
		err := handlePart(ctx, thread, date, reg)
		if err == nil {
			reg.Processed = true
		} else {
			log.Error("[worker ", thread, "] Error processing part ", reg.Name, " version ", reg.Date, ": ", err)
		}
		time.Sleep(1 * time.Second)

		if len(eregs.SuppContentURL) > 0 {
			log.Debug("[worker ", thread, "] Processing supplemental part ", reg.Name, " version ", reg.Date)
			err := handleSupplementalPart(ctx, thread, reg)
			if err == nil {
				reg.Processed = true
			} else {
				log.Error("[worker ", thread, "] Error processing supplemental part ", reg.Name, " version ", reg.Date, ": ", err)
			}
			time.Sleep(1 * time.Second)
		}
	}

	wg.Done()
}

func handlePart(ctx context.Context, thread int, date time.Time, reg *eregs.Part) error {
	start := time.Now()

	log.Debug("[worker ", thread, "] Fetching structure for part ", reg.Name, " version ", reg.Date)
	sbody, err := ecfr.FetchStructure(ctx, date.Format("2006-01-02"), reg.Title, &ecfr.PartOption{reg.Name})

	if err != nil {
		return err
	}

	log.Trace("[worker ", thread, "] Decoding structure for part ", reg.Name, " version ", reg.Date)
	sd := json.NewDecoder(sbody)
	if err := sd.Decode(reg.Structure); err != nil {
		return err
	}

	log.Debug("[worker ", thread, "] Fetching full document for part ", reg.Name, " version ", reg.Date)
	body, err := ecfr.FetchFull(ctx, reg.Date, reg.Title, &ecfr.PartOption{reg.Name})
	if err != nil {
		return err
	}

	log.Trace("[worker ", thread, "] Decoding full structure for part ", reg.Name, " version ", reg.Date)
	d := xml.NewDecoder(body)
	if err := d.Decode(reg.Document); err != nil {
		return err
	}

	log.Debug("[worker ", thread, "] Running post process on structure for part ", reg.Name, " version ", reg.Date)
	if err := reg.Document.PostProcess(); err != nil {
		return err
	}

	log.Debug("[worker ", thread, "] Posting part ", reg.Name, " version ", reg.Date, " to eRegs")
	if err := eregs.PostPart(ctx, reg); err != nil {
		return err
	}

	log.Debug("[worker ", thread, "] Successfully processed part ", reg.Name, " version ", reg.Date, " in ", time.Since(start))
	return nil
}

func handleSupplementalPart(ctx context.Context, thread int, reg *eregs.Part) error {
	log.Debug("[worker ", thread, "] Extracting supplemental content structure ", reg.Name, " version ", reg.Date)
	supplementalPart, err := ecfr.ExtractStructure(*reg.Structure)
	if err != nil {
		return err
	}

	log.Debug("[worker ", thread, "] Posting supplemental content structure ", reg.Name, " version ", reg.Date, " to eRegs")
	if err := eregs.PostSupplementalPart(ctx, supplementalPart); err != nil {
		return err
	}

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
