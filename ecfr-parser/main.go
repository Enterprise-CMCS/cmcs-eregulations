package main

import (
	"context"
	"encoding/xml"
	"flag"
	"fmt"
	"io"
	"log"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/eregs"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/parseXML"
)

const TIMELIMIT = 160 * time.Second

var (
	title           int
	subchapter      SubchapterArg
	individualParts PartsArg
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

// ./a TITLE -s SUBCHAPTER-CHAPTER -p PART1,PART2,...
// -title TITLE -subchapter CHAP-SUB -parts PART1, PART2

func init() {
	flag.IntVar(&title, "title", -1, "The number of the regulation title to be loaded")
	flag.Var(&subchapter, "subchapter", "A chapter and subchapter separated by a dash, e.g. IV-C")
	flag.Var(&individualParts, "parts", "A comma-separated list of parts to load, e.g. 457,460")
	flag.Parse()

	if title < 0 {
		log.Fatal("Title flag is required and must be greater than 0.")
	}
}

func main() {

	log.SetFlags(log.Lshortfile | log.LstdFlags)

	ctx, cancel := context.WithTimeout(context.Background(), TIMELIMIT)
	defer cancel()

	start := time.Now()
	defer func() {
		log.Println("Run time:", time.Since(start))
	}()

	today := time.Now()

	log.Println("[DEBUG] fetching Parts")

	var parts []string
	if subchapter != nil {
		var err error
		parts, err = ecfr.ExtractSubchapterParts(ctx, today, title, ecfr.Subchapter(subchapter[0], subchapter[1]))
		if err != nil {
			log.Fatal(err)
		}
	}
	parts = append(parts, individualParts...)

	if len(parts) < 1 {
		log.Fatal("Some number of parts must be specified")
	}

	var wg sync.WaitGroup

	for _, part := range parts {
		versions, err := ecfr.ExtractPartVersions(ctx, title, ecfr.Part(part))
		if err != nil {
			log.Fatal(err)
		}
		for date, _ := range versions {
			d, err := time.Parse("2006-01-02", date)
			if err != nil {
				log.Fatal(err)
			}
			wg.Add(1)
			go func(ctx context.Context, part string, date time.Time) {
				defer wg.Done()
				handlePart(ctx, part, date)
			}(ctx, part, d)
		}
	}

	wg.Wait()
}

func handlePart(ctx context.Context, part string, date time.Time) {

	s, err := ecfr.FetchStructure(ctx, date, title, ecfr.Part(part))
	if err != nil {
		log.Fatal("[ERROR] ", err, date, part)
		return
	}

	reg := &eregs.Part{
		Title:     strconv.Itoa(title),
		Name:      part,
		Date:      date.Format("2006-01-02"),
		Structure: s,
		Document:  &parseXML.Part{},
	}

	body, err := ecfr.FetchFull(ctx, date, title, ecfr.Part(part))
	if err != nil {
		if err.Error() == "404" {
			log.Println("[ERROR] not found", part, date)
			return
		}
		log.Fatal(err)
	}

	d := xml.NewDecoder(body)

	if err := d.Decode(reg.Document); err != nil {
		log.Fatal(err)
	}

	if reg.Document == nil {
		log.Fatal("[ERROR] nil part", date, part)
	}

	if err := reg.Document.PostProcess(); err != nil {
		log.Fatal("[ERROR] ", err, date, part)
		return
	}

	resp, err := eregs.PostPart(ctx, reg)
	if err != nil {

		if resp != nil {
			defer resp.Body.Close()
			response, err := io.ReadAll(resp.Body)
			if err != nil {
				log.Println("[ERROR]", err)
			}
			log.Println(string(response))
		}
		log.Fatal("[ERROR]", err, date, part)
	}

}
