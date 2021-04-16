package main

import (
	"encoding/json"
	"encoding/xml"
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

type Subpart struct {
	Header   string          `xml:"HEAD"`
	Type     string          `xml:"TYPE,attr"`
	Children SubpartChildren `xml:",any"`
}

// subpart > sections & subjgrps

type Section struct {
	Header   string          `xml:"HEAD"`
	Children SectionChildren `xml:",any"`
}

type Paragraph struct {
	Content string `xml:",innerxml"`
}

type Extract struct {
	Content string `xml:",innerxml"`
}

type Citation string

// section > paragraphs

type PartChildren []interface{}
type SubpartChildren []interface{}
type SectionChildren []interface{}

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
		//return fmt.Errorf("Unknown XML type in Part: %+v", start)
		d.Skip()
	}

	return nil
}

func (c *SubpartChildren) UnmarshalXML(d *xml.Decoder, start xml.StartElement) error {
	switch start.Name.Local {
	case "DIV8":
		child := &Section{}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	default:
		//return fmt.Errorf("Unknown XML type in Subpart: %+v", start)
		d.Skip()
	}
	return nil
}

func (c *SectionChildren) UnmarshalXML(d *xml.Decoder, start xml.StartElement) error {
	switch start.Name.Local {
	case "P":
		child := &Paragraph{}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	case "EXTRACT":
		child := &Extract{}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	case "CITA":
		var child Citation
		if err := d.DecodeElement(&child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	default:
		//return fmt.Errorf("Unknown XML type in Section: %+v", start)
		d.Skip()
	}

	return nil
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
