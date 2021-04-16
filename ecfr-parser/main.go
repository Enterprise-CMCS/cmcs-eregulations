package main

import (
	"encoding/json"
	"encoding/xml"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"time"
)

func URLMustParse(s string) *url.URL {
	u, err := url.Parse(s)
	if err != nil {
		log.Fatal(err)
	}
	return u
}

var ecfrSite = URLMustParse("https://ecfr.federalregister.gov/api/versioner/v1/")
var ecfrFullXML = "full/%s/title-%d.xml?part=%d"

type Part struct {
	Title     int
	Name      int
	Date      time.Time
	Header    string       `xml:"HEAD"`
	Authority string       `xml:"AUTH>PSPACE"`
	Source    string       `xml:"SOURCE>PSPACE"`
	Children  PartChildren `xml:",any"`
}

func (p *Part) url() (string, error) {
	path, err := url.Parse(fmt.Sprintf(ecfrFullXML, p.Date.Format("2006-01-02"), p.Title, p.Name))

	if err != nil {
		return "", err
	}

	u := ecfrSite.ResolveReference(path)

	return u.String(), nil
}

func (p *Part) fetch() (io.ReadCloser, error) {
	path, err := p.url()
	if err != nil {
		return nil, err
	}

	resp, err := http.Get(path)
	if err != nil {
		return nil, err
	}
	return resp.Body, nil
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

func main() {
	today := time.Now()
	p := &Part{
		Title: 42,
		Name:  433,
		Date:  today,
	}
	start := time.Now()
	log.Println("[DEBUG] fetching part")
	body, err := p.fetch()
	if err != nil {
		log.Fatal(err)
	}
	defer body.Close()

	d := xml.NewDecoder(body)

	log.Println("[DEBUG] Decoding part")
	if err := d.Decode(p); err != nil {
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
