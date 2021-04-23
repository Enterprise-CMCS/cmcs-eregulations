package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/parseXML"
)

func main() {
	log.SetFlags(log.Lshortfile | log.LstdFlags)

	start := time.Now()

	log.Println("[DEBUG] fetching Versions")
	vbody, err := ecfr.FetchVersions(42)
	if err != nil {
		log.Fatal(err)
	}
	defer vbody.Close()
	vs := &ecfr.Versions{}
	d := json.NewDecoder(vbody)
	if err := d.Decode(vs); err != nil {
		log.Fatal(err)
	}
	versions := ecfr.PartVersions(vs.ContentVersions)
	log.Println(versions)
	var wg sync.WaitGroup
	output := make(chan []byte)
	go func() {
		for obj := range output {
			fmt.Println(string(obj))
		}
	}()

	sbody, err := ecfr.FetchStructure("2021-04-20", 42, ecfr.Subchapter("C", "IV"))
	if err != nil {
		log.Fatal(err)
	}
	defer sbody.Close()
	s := &ecfr.Structure{}
	sd := json.NewDecoder(sbody)
	if err := sd.Decode(s); err != nil {
		log.Fatal(err)
	}
	parts := ecfr.SubchapterParts(s)
	log.Println(parts)

	for _, part := range parts {
		for date, _ := range versions[part.Identifier] {
			wg.Add(1)
			go func(part string, date string, output chan []byte) {
				defer wg.Done()
				handlePart(part, date, output)
			}(part.Identifier, date, output)
		}
	}

	wg.Wait()
	close(output)

	log.Println("Run time:", time.Since(start))
}

func handlePart(part string, date string, output chan []byte) {
	body, err := ecfr.FetchFull(date, 42, ecfr.Part(part))
	if err != nil {
		if err.Error() == "429" {
			time.Sleep(2 * time.Second)
			handlePart(part, date, output)
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
	enc.SetIndent("", "  ")
	if err := enc.Encode(p); err != nil {
		log.Fatal(err)
	}
	output <- b.Bytes()
}
