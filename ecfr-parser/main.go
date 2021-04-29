package main

import (
	"context"
	"encoding/json"
	"encoding/xml"
	"flag"
	"fmt"
	"io"
	"log"
	"strings"
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

func init() {
	flag.IntVar(&title, "title", -1, "The number of the regulation title to be loaded")
	flag.Var(&subchapter, "subchapter", "A chapter and subchapter separated by a dash, e.g. IV-C")
	flag.Var(&individualParts, "parts", "A comma-separated list of parts to load, e.g. 457,460")
	flag.StringVar(&eregs.BaseURL, "eregs-url", "http://localhost:8080/v2/", "A url specifying where to send eregs parts")
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
		log.Println("[DEBUG] run time:", time.Since(start))
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

	versions, err := ecfr.ExtractVersions(ctx, title)
	if err != nil {
		log.Fatal(err)
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
			if err := handlePart(ctx, reg); err != nil {
				log.Fatal(err)
			}
		}
	}
}

func handlePart(ctx context.Context, reg *eregs.Part) error {

	sbody, err := ecfr.FetchStructure(ctx, reg.Date, reg.Title, ecfr.PartOption(reg.Name))
	if err != nil {
		return err
	}

	sd := json.NewDecoder(sbody)
	if err := sd.Decode(reg.Structure); err != nil {
		return err
	}

	body, err := ecfr.FetchFull(ctx, reg.Date, reg.Title, ecfr.PartOption(reg.Name))
	if err != nil {
		return err
	}

	d := xml.NewDecoder(body)

	if err := d.Decode(reg.Document); err != nil {
		return err
	}

	if err := reg.Document.PostProcess(); err != nil {
		return err
	}

	resp, err := eregs.PostPart(ctx, reg)
	if err != nil {
		if resp != nil {
			defer resp.Body.Close()
			response, e := io.ReadAll(resp.Body)
			if e != nil {
				log.Println("[ERROR]", e)
			}
			return fmt.Errorf("%s | %s", err.Error(), string(response))
		}
		return err
	}
	return nil
}
