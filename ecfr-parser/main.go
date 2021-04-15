package main

import (
	"encoding/json"
	"encoding/xml"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
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
	Header    string `xml:"HEAD"`
	Authority string `xml:"AUTH>PSPACE"`
}

func (p *Part) url() (string, error) {
	// u/part.Date/title-part.Title.xml?part=part.Name
	path, err := url.Parse(fmt.Sprintf(ecfrFullXML, p.Date.Format("2006-01-02"), p.Title, p.Name))

	if err != nil {
		return "", err
	}

	u := ecfrSite.ResolveReference(path)

	return u.String(), nil
}

func (p *Part) fetch() (io.ReadCloser, error) {
	// u/part.Date/title-part.Title.xml?part=part.Name
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

func main() {
	today, _ := time.Parse("2006-01-02", "2021-04-15")
	p := &Part{
		Title: 42,
		Name:  433,
		Date:  today,
	}
	body, err := p.fetch()
	if err != nil {
		log.Fatal(err)
	}
	defer body.Close()

	d := xml.NewDecoder(body)

	if err := d.Decode(p); err != nil {
		log.Fatal(err)
	}

	j, err := json.MarshalIndent(p, "", "  ")
	if err != nil {
		log.Fatal(err)
	}

	log.Println(string(j))
}
