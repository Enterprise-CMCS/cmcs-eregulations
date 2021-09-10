package ecfr

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"time"
)

const dateFormat = "2006-01-02"
const timeout = 10 * time.Second

var (
	ecfrSite         = urlMustParse("https://ecfr.federalregister.gov/api/versioner/v1/")
	ecfrFullXML      = "full/%s/title-%d.xml"
	ecfrVersionsXML  = "versions/title-%d"
	ecfrStructureXML = "structure/%s/title-%d.json"
)

var client = &http.Client{
	Transport: &http.Transport{},
}

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

func fetch(ctx context.Context, path *url.URL, opts []FetchOption) (io.Reader, error) {
	path.RawQuery = buildQuery(opts)

	u := ecfrSite.ResolveReference(path)

	c, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	req, err := http.NewRequestWithContext(c, http.MethodGet, u.String(), nil)
	if err != nil {
		return nil, err
	}

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode != 200 {
		if resp.StatusCode == http.StatusTooManyRequests || resp.StatusCode == http.StatusBadGateway {
			time.Sleep(2 * time.Second)
			return fetch(ctx, path, opts)
		}
		return nil, fmt.Errorf("%s %d", u.String(), resp.StatusCode)
	}
	defer resp.Body.Close()
	b, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	body := bytes.NewBuffer(b)

	return body, nil
}

func FetchFull(ctx context.Context, date string, title int, opts ...FetchOption) (io.Reader, error) {
	path, err := url.Parse(fmt.Sprintf(ecfrFullXML, date, title))
	if err != nil {
		return nil, err
	}
	return fetch(ctx, path, opts)
}

func FetchStructure(ctx context.Context, date string, title int, opts ...FetchOption) (io.Reader, error) {
	path, err := url.Parse(fmt.Sprintf(ecfrStructureXML, date, title))
	if err != nil {
		return nil, err
	}
	return fetch(ctx, path, opts)
}

func FetchVersions(ctx context.Context, title int, opts ...FetchOption) (io.Reader, error) {
	path, err := url.Parse(fmt.Sprintf(ecfrVersionsXML, title))
	if err != nil {
		return nil, err
	}
	return fetch(ctx, path, opts)
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

func PartOption(part string) *partOption {
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
