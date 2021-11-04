package main

import (
	"context"
	"encoding/json"
	"encoding/xml"
	"flag"
	"fmt"
	"io"
	"strings"
	"sync"
	"time"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/eregs"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/parseXML"

	log "github.com/sirupsen/logrus"
)

const TIMELIMIT = 5000 * time.Second

var (
	attempts        int
	title           int
	subchapter      SubchapterArg
	individualParts PartsArg
	loglevel        string
	threads         int
)

type SubchapterArg []string

func (sc *SubchapterArg) String() string {
	return strings.Join(*sc, "-")
}

func (sc *SubchapterArg) Set(s string) error {
	*sc = strings.Split(s, "-")
	if len(*sc) != 2 {
		return fmt.Errorf("Subchapter is expected to be of the form <Roman Numeral>-<Letter>")
	}
	return nil
}

type PartsArg []string

func (pa *PartsArg) String() string {
	return strings.Join(*pa, ",")
}

func (pa *PartsArg) Set(s string) error {
	*pa = strings.Split(s, ",")

	return nil
}

func init() {
	flag.IntVar(&title, "title", -1, "The number of the regulation title to be loaded")
	flag.Var(&subchapter, "subchapter", "A chapter and subchapter separated by a dash, e.g. IV-C")
	flag.Var(&individualParts, "parts", "A comma-separated list of parts to load, e.g. 457,460")
	flag.StringVar(&eregs.BaseURL, "eregs-url", "http://localhost:8080/v2/", "A url specifying where to send eregs parts")
	flag.IntVar(&threads, "threads", 3, "Number of parts to process simultaneously.")
	flag.IntVar(&attempts, "attempts", 1, "The number of times to attempt regulation loading")
	flag.StringVar(&loglevel, "loglevel", "warn", "Logging severity level. One of: fatal, error, warn, info, debug, trace.")
	flag.BoolVar(&parseXML.LogParseErrors, "log-parse-errors", true, "Output errors encountered while parsing.")
	flag.Parse()

	if title < 0 {
		log.Fatal("[main] Title flag is required and must be greater than 0.")
	}

	level := log.WarnLevel
	switch loglevel {
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
	}
	log.SetLevel(level)
}

func main() {
	for i := 0; i < attempts; i++ {
		if err := run(); err == nil {
			break
		} else if i == attempts - 1 {
			log.Fatal("[main] Failed to load regulations ", attempts, " times. Error: ", err)
		} else {
			log.Error("[main] Failed to load regulations. Retrying", attempts - i - 1, "more times. Error: ", err)
		}
	}
}

func run() error {
	ctx, cancel := context.WithTimeout(context.Background(), TIMELIMIT)
	defer cancel()

	start := time.Now()
	defer func() {
		log.Debug("[main] Run time:", time.Since(start))
	}()

	today := time.Now()

	log.Info("[main] Fetching parts list...")

	var parts []string
	if subchapter != nil {
		log.Debug("[main] Fetching subchapter ", subchapter, " parts list...")
		var err error
		parts, err = ecfr.ExtractSubchapterParts(ctx, today, title, ecfr.Subchapter(subchapter[0], subchapter[1]))
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
		return err
	}

	log.Info("[main] Fetching and processing parts...")
	ch := make(chan *eregs.Part)
	var wg sync.WaitGroup
	for i := 0; i < threads; i++ {
		wg.Add(1)
		go startHandlePartWorker(i, ch, &wg, ctx, today)
	}

	for _, part := range parts {
		for date := range versions[part] {
			reg := &eregs.Part{
				Title:     title,
				Name:      part,
				Date:      date,
				Structure: &ecfr.Structure{},
				Document:  &parseXML.Part{},
			}
			ch <- reg
		}
	}

	log.Debug("[main] Waiting until all parts are finished processing.")
	close(ch)
	wg.Wait()
	log.Info("[main] All parts finished processing!")

	return nil
}

func startHandlePartWorker(thread int, ch chan *eregs.Part, wg *sync.WaitGroup, ctx context.Context, date time.Time) {
	for reg := range ch {
		log.Debug("[worker ", thread, "] Processing part ", reg.Name)
		err := handlePart(thread, ctx, date, reg)
		if err != nil {
			log.Error("[worker ", thread, "] Error processing part ", reg.Name, ": ", err)
		}
		time.Sleep(1 * time.Second)
	}

	wg.Done()
}

func handlePart(thread int, ctx context.Context, date time.Time, reg *eregs.Part) error {
	log.Debug("[worker ", thread, "] Fetching structure for part ", reg.Name)
	sbody, err := ecfr.FetchStructure(ctx, date.Format("2006-01-02"), reg.Title, ecfr.PartOption(reg.Name))
	if err != nil {
		return err
	}

	log.Trace("[worker ", thread, "] Decoding structure for part ", reg.Name)
	sd := json.NewDecoder(sbody)
	if err := sd.Decode(reg.Structure); err != nil {
		return err
	}

	log.Debug("[worker ", thread, "] Fetching full document for part ", reg.Name)
	body, err := ecfr.FetchFull(ctx, reg.Date, reg.Title, ecfr.PartOption(reg.Name))
	if err != nil {
		return err
	}

	log.Trace("[worker ", thread, "] Decoding full structure for part ", reg.Name)
	d := xml.NewDecoder(body)
	if err := d.Decode(reg.Document); err != nil {
		return err
	}

	log.Debug("[worker ", thread, "] Running post process on structure for part ", reg.Name)
	if err := reg.Document.PostProcess(); err != nil {
		return err
	}

	log.Debug("[worker ", thread, "] Posting part ", reg.Name, " to eRegs")
	resp, err := eregs.PostPart(ctx, reg)
	if err != nil {
		if resp != nil {
			defer resp.Body.Close()
			response, e := io.ReadAll(resp.Body)
			if e != nil {
				log.Error(e)
			}
			return fmt.Errorf("%s | %s", err.Error(), string(response))
		}
		return err
	}

	log.Debug("[worker ", thread, "] Successfully processed part ", reg.Name)
	return nil
}
