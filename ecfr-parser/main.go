package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/parseXML"
)

const TIMELIMIT = 60 * time.Second

func main() {
	log.SetFlags(log.Lshortfile | log.LstdFlags)
	title := 42

	start := time.Now()

	log.Println("[DEBUG] fetching Versions")
	versions, err := ecfr.ExtractPartVersions(title)
	if err != nil {
		log.Fatal(err)
	}
	log.Println(versions)

	parts, err := ecfr.ExtractSubchapterParts(start, title, "IV", "C")
	if err != nil {
		log.Fatal(err)
	}
	log.Println(parts)

	var wg sync.WaitGroup
	output := make(chan []byte)
	go func() {
		for obj := range output {
			fmt.Println(string(obj))
		}
	}()

	ctx, cancel := context.WithTimeout(context.Background(), TIMELIMIT)
	defer cancel()
	for _, part := range parts {
		for date, _ := range versions[part.Identifier] {
			wg.Add(1)
			go func(ctx context.Context, part string, dateString string, output chan []byte) {
				defer wg.Done()
				date, err := time.Parse("2006-01-02", dateString)
				if err != nil {
					log.Fatal(err)
				}
				handlePart(ctx, part, date, output)
			}(ctx, part.Identifier, date, output)
		}
	}

	wg.Wait()
	close(output)

	log.Println("Run time:", time.Since(start))
}

func handlePart(ctx context.Context, part string, date time.Time, output chan []byte) {
	if ctx.Err() != nil {
		log.Println("[ERROR]", ctx.Err())
		return
	}
	body, err := ecfr.FetchFull(date, 42, ecfr.Part(part))
	if err != nil {
		if err.Error() == "429" {
			time.Sleep(2 * time.Second)
			handlePart(ctx, part, date, output)
			return
		}
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

	b := bytes.NewBuffer([]byte{})
	enc := json.NewEncoder(b)
	enc.SetEscapeHTML(false)
	if err := enc.Encode(p); err != nil {
		log.Fatal(err)
	}
	output <- b.Bytes()
}
