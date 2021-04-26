package main

import (
	"bytes"
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
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

	start := time.Now()
	defer func() {
		log.Println("Run time:", time.Since(start))
	}()

	today := time.Now()

	log.Println("[DEBUG] fetching Parts")

	var parts []string
	if subchapter != nil {
		var err error
		parts, err = ecfr.ExtractSubchapterParts(today, title, ecfr.Subchapter(subchapter[0], subchapter[1]))
		if err != nil {
			log.Fatal(err)
		}
	}
	parts = append(parts, individualParts...)

	if len(parts) < 1 {
		log.Fatal("Some number of parts must be specified")
	}

	var wg sync.WaitGroup

	ctx, cancel := context.WithTimeout(context.Background(), TIMELIMIT)
	defer cancel()
	for _, part := range parts {
		versions, err := ecfr.ExtractPartVersions(title, ecfr.Part(part))
		if err != nil {
			log.Fatal(err)
		}
		for date, _ := range versions {
			wg.Add(1)
			go func(ctx context.Context, part string, dateString string) {
				defer wg.Done()
				date, err := time.Parse("2006-01-02", dateString)
				if err != nil {
					log.Fatal(err)
				}
				handlePart(ctx, part, date)
			}(ctx, part, date)
		}
	}

	wg.Wait()
}

func printResults(output chan []byte) {
	for obj := range output {
		fmt.Println(string(obj))
	}
}

func handlePart(ctx context.Context, part string, date time.Time) {
	if ctx.Err() != nil {
		log.Println("[ERROR]", ctx.Err())
		return
	}
	body, err := ecfr.FetchFull(date, title, ecfr.Part(part))
	if err != nil {
		if err.Error() == "404" {
			log.Println("[ERROR] not found", part, date)
			return
		}
		log.Fatal(err)
	}
	defer body.Close()

	log.Println("[DEBUG] parsing", date, part)
	p, err := parseXML.ParsePart(body)
	if err != nil {
		log.Fatal("[ERROR] ", err, date, part)
		return
	}

	if err := p.PostProcess(); err != nil {
		log.Fatal("[ERROR] ", err, date, part)
		return
	}

	s, err := ecfr.FetchStructure(date, title, ecfr.Part(part))
	if err != nil {
		log.Fatal("[ERROR] ", err, date, part)
		return
	}

	p.Structure = s

	if p == nil {
		log.Fatal("[ERROR] nil part", p, s, date, part)
	}

	buff := bytes.NewBuffer([]byte{})
	enc := json.NewEncoder(buff)
	enc.SetEscapeHTML(false)
	reg := &struct {
		Title    string         `json:"title"`
		Name     string         `json:"name"`
		Date     string         `json:"date"`
		Document *parseXML.Part `json:"document"`
	}{
		strconv.Itoa(title),
		part,
		date.Format("2006-01-02"),
		p,
	}

	if err := enc.Encode(reg); err != nil {
		log.Fatal(err)
	}

	b := buff.Bytes()

	req, err := http.NewRequest(http.MethodPut, fmt.Sprintf("http://localhost:8080/v2/%s/title/%s/part/%s", reg.Date, reg.Title, reg.Name), bytes.NewReader(b))
	if err != nil {
		log.Fatal(err)
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		log.Fatal(err)
	}

	if resp.StatusCode >= 400 {
		resp, err = http.Post("http://localhost:8080/v2/", "application/json", bytes.NewReader(b))
		if err != nil {
			log.Fatal(err)
		}
	}

	if resp.StatusCode >= 400 {
		log.Fatal(resp.StatusCode, string(b))
	}
}
