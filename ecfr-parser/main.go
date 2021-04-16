package main

import (
	"encoding/json"
	"log"
	"os"
	"time"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/parseXML"
)

func main() {
	today := time.Now()

	start := time.Now()
	log.Println("[DEBUG] fetching part")
	body, err := ecfr.FetchPart(today, 42, ecfr.Part(433))
	if err != nil {
		log.Fatal(err)
	}
	defer body.Close()

	p, err := parseXML.ParsePart(body)
	if err != nil {
		log.Fatal(err)
	}

	log.Println("[DEBUG] Marshaling JSON of Part")
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	if err := enc.Encode(p); err != nil {
		log.Fatal(err)
	}

	log.Println("Run time:", time.Since(start))
}
