package main

import (
	"encoding/json"
	"encoding/xml"
	"fmt"
	"io"
	"log"
	"os"
	"time"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
)

type Part struct {
	XMLName   xml.Name     `xml:"DIV5"`
	Name      string       `xml:"N,attr"`
	Type      string       `xml:"TYPE,attr"`
	Header    string       `xml:"HEAD"`
	Authority string       `xml:"AUTH>PSPACE"`
	Source    string       `xml:"SOURCE>PSPACE"`
	Children  PartChildren `xml:",any"`
}

type PartChildren []interface{}

func (c *PartChildren) UnmarshalXML(d *xml.Decoder, start xml.StartElement) error {
	switch start.Name.Local {
	case "DIV6":
		child := &Subpart{}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	case "DIV8":
		child := &Section{}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	default:
		return fmt.Errorf("uknown xml type in Part: %+v", start)
	}

	return nil
}

type Subpart struct {
	Header string `xml:"HEAD"`
}

type Section struct {
	Header string `xml:"HEAD"`
}

func ParsePart(b io.ReadCloser) (*Part, error) {
	d := xml.NewDecoder(b)

	p := &Part{}
	log.Println("[DEBUG] Decoding part")
	if err := d.Decode(p); err != nil {
		return p, err
	}
	return p, nil
}

func main() {
	today := time.Now()

	start := time.Now()
	log.Println("[DEBUG] fetching part")
	body, err := ecfr.FetchPart(today, 42, ecfr.Part(433))
	if err != nil {
		log.Fatal(err)
	}
	defer body.Close()

	p, err := ParsePart(body)
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
