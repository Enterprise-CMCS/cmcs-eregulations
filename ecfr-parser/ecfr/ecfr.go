package ecfr

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"strconv"
	"time"
)

const dateFormat = "2006-01-02"

var (
	ecfrSite    = urlMustParse("https://ecfr.federalregister.gov/api/versioner/v1/")
	ecfrFullXML = "full/%s/title-%d.xml"
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

func FetchPart(date time.Time, title int, opts ...FetchOption) (io.ReadCloser, error) {
	path, err := url.Parse(fmt.Sprintf(ecfrFullXML, date.Format(dateFormat), title))
	if err != nil {
		return nil, err
	}

	path.RawQuery = buildQuery(opts)

	u := ecfrSite.ResolveReference(path)

	resp, err := http.Get(u.String())
	if err != nil {
		return nil, err
	}

	return resp.Body, nil
}

type FetchOption interface {
	Values() url.Values
}

type partOption struct {
	part int
}

func (p *partOption) Values() url.Values {
	v := url.Values{}
	v.Set("part", strconv.Itoa(p.part))
	return v
}

func Part(part int) FetchOption {
	return &partOption{
		part: part,
	}
}
