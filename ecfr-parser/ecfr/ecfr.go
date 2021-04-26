package ecfr

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"time"
)

const dateFormat = "2006-01-02"

var (
	ecfrSite         = urlMustParse("https://ecfr.federalregister.gov/api/versioner/v1/")
	ecfrFullXML      = "full/%s/title-%d.xml"
	ecfrVersionsXML  = "versions/title-%d.json"
	ecfrStructureXML = "structure/%s/title-%d.json"
)

func urlMustParse(s string) *url.URL {
	u, err := url.Parse(s)
	if err != nil {
		log.Fatal(err)
	}
	return u
}

func buildQuery(opts []FetchOption) string {
	q := url.Values{}
	for _, opt := range opts {
		v := opt.Values()
		for key, _ := range v {
			q.Set(key, v.Get(key))
		}
	}
	return q.Encode()
}

func fetch(path *url.URL, opts []FetchOption) (io.ReadCloser, error) {
	path.RawQuery = buildQuery(opts)

	u := ecfrSite.ResolveReference(path)

	resp, err := http.Get(u.String())
	if err != nil {
		return nil, err
	}
	if resp.StatusCode != 200 {
		if resp.StatusCode == http.StatusTooManyRequests || resp.StatusCode == http.StatusBadGateway {
			time.Sleep(2 * time.Second)
			return fetch(path, opts)
		}
		return nil, fmt.Errorf("%d", resp.StatusCode)
	}

	return resp.Body, nil
}

func FetchFull(date time.Time, title int, opts ...FetchOption) (io.ReadCloser, error) {
	path, err := url.Parse(fmt.Sprintf(ecfrFullXML, date.Format("2006-01-02"), title))
	if err != nil {
		return nil, err
	}
	return fetch(path, opts)
}

func FetchStructure(date time.Time, title int, opts ...FetchOption) (*Structure, error) {
	path, err := url.Parse(fmt.Sprintf(ecfrStructureXML, date.Format("2006-01-02"), title))
	if err != nil {
		return nil, err
	}
	sbody, err := fetch(path, opts)
	if err != nil {
		return nil, err
	}
	defer sbody.Close()
	s := &Structure{}
	sd := json.NewDecoder(sbody)
	if err := sd.Decode(s); err != nil {
		return nil, err
	}
	return s, nil
}

func FetchVersions(title int, opts ...FetchOption) (io.ReadCloser, error) {
	path, err := url.Parse(fmt.Sprintf(ecfrVersionsXML, title))
	if err != nil {
		return nil, err
	}
	return fetch(path, opts)
}

type FetchOption interface {
	Values() url.Values
}

type partOption struct {
	part string
}

func (p *partOption) Values() url.Values {
	v := url.Values{}
	v.Set("part", p.part)
	return v
}

func Part(part string) *partOption {
	return &partOption{
		part: part,
	}
}

type subchapterOption struct {
	chapter    string
	subchapter string
}

func (p *subchapterOption) Values() url.Values {
	v := url.Values{}
	v.Set("chapter", p.chapter)
	v.Set("subchapter", p.subchapter)
	return v
}

func Subchapter(chapter string, subchapter string) *subchapterOption {
	return &subchapterOption{
		chapter:    chapter,
		subchapter: subchapter,
	}
}
