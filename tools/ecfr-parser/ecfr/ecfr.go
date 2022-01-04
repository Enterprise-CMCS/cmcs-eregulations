package ecfr

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"time"

	log "github.com/sirupsen/logrus"
)

const dateFormat = "2006-01-02"
const timeout = 10 * time.Second

var (
	ecfrSite          = urlMustParse("https://ecfr.gov/api/versioner/v1/")
	ecfrFullXML       = "full/%s/title-%d.xml"
	ecfrVersionsXML   = "versions/title-%d"
	ecfrStructureJSON = "structure/%s/title-%d.json"
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
		for key := range v {
			q.Set(key, v.Get(key))
		}
	}
	return q.Encode()
}

func fetch(ctx context.Context, path *url.URL, opts []FetchOption) (io.Reader, error) {
	path.RawQuery = buildQuery(opts)
	u := ecfrSite.ResolveReference(path)

	log.Trace("[ecfr] Attempting fetch from ", u.String())
	start := time.Now()

	c, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	req, err := http.NewRequestWithContext(c, http.MethodGet, u.String(), nil)
	if err != nil {
		return nil, fmt.Errorf("from `http.NewRequestWithContext`: %+v", err)
	}

	req.Header.Set("User-Agent", "E-regs for "+os.Getenv("NAME"))
	log.Trace("[ecfr] User agent is: ", req.Header.Get("User-Agent"))

	log.Trace("[ecfr] Connecting to ", u.String())
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("Client failed to connect: %+v", err)
	}
    defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("Received status code %d from %s", resp.StatusCode, u.String())
	}

	b, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("Failed to read response body: %+v", err)
	}
	body := bytes.NewBuffer(b)

	log.Trace("[ecfr] Received ", len(b), " bytes in ", time.Since(start), " from ", u.String())
	return body, nil
}

// FetchFull fetches the full regulation from eCFR
func FetchFull(ctx context.Context, date string, title int, opts ...FetchOption) (io.Reader, error) {
	path, err := url.Parse(fmt.Sprintf(ecfrFullXML, date, title))
	if err != nil {
		return nil, err
	}
	return fetch(ctx, path, opts)
}

// FetchStructure fetches the structure for a given title and options
func FetchStructure(ctx context.Context, date string, title int, opts ...FetchOption) (io.Reader, error) {
	path, err := url.Parse(fmt.Sprintf(ecfrStructureJSON, date, title))
	if err != nil {
		return nil, err
	}
	return fetch(ctx, path, opts)
}

// FetchVersions fetches the available versions for a given title
func FetchVersions(ctx context.Context, title int, opts ...FetchOption) (io.Reader, error) {
	path, err := url.Parse(fmt.Sprintf(ecfrVersionsXML, title))
	if err != nil {
		return nil, err
	}
	return fetch(ctx, path, opts)
}

// FetchOption defines optional values for the fetch process
type FetchOption interface {
	Values() url.Values
}

// PartOption is a struct that represents a string referring to the regulation Part
type PartOption struct {
	Part string
}

// Values inserts the Partoption.Part into a urlValues struct
func (p *PartOption) Values() url.Values {
	v := url.Values{}
	v.Set("part", p.Part)
	return v
}

// SubchapterOption is a struct defining the Chapter and Subchapter
type SubchapterOption struct {
	Chapter    string
	Subchapter string
}

// Values returns a url.Values for the Chapter and SubChapter
func (p *SubchapterOption) Values() url.Values {
	v := url.Values{}
	v.Set("chapter", p.Chapter)
	v.Set("subchapter", p.Subchapter)
	return v
}
