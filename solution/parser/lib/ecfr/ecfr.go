package ecfr

import (
	"context"
	"fmt"
	"io"
	"net/url"
	"path"

	"github.com/cmsgov/cmcs-eregulations/lib/network"
)

// EcfrSite is the base URL for accessing the eCFR API
var EcfrSite = "https://ecfr.gov/api/versioner/v1/"

var (
	ecfrFullXML       = "full/%s/title-%d.xml"
	ecfrVersionsXML   = "versions/title-%d"
	ecfrStructureJSON = "structure/current/title-%d.json"
)

// FetchFull fetches the full regulation from eCFR
func FetchFull(ctx context.Context, date string, title int, opts ...network.FetchOption) (io.Reader, int, error) {
	ecfrURL, err := url.Parse(EcfrSite)
	if err != nil {
		return nil, -1, err
	}
	ecfrURL.Path = path.Join(ecfrURL.Path, fmt.Sprintf(ecfrFullXML, date, title))
	return network.FetchWithOptions(ctx, ecfrURL, false, opts, nil)
}

// FetchStructure fetches the structure for a given title and options
func FetchStructure(ctx context.Context, title int, opts ...network.FetchOption) (io.Reader, int, error) {
	ecfrURL, err := url.Parse(EcfrSite)
	if err != nil {
		return nil, -1, err
	}
	ecfrURL.Path = path.Join(ecfrURL.Path, fmt.Sprintf(ecfrStructureJSON, title))
	return network.FetchWithOptions(ctx, ecfrURL, false, opts, nil)
}

// FetchVersions fetches the available versions for a given title
func FetchVersions(ctx context.Context, title int, opts ...network.FetchOption) (io.Reader, int, error) {
	ecfrURL, err := url.Parse(EcfrSite)
	if err != nil {
		return nil, -1, err
	}
	ecfrURL.Path = path.Join(ecfrURL.Path, fmt.Sprintf(ecfrVersionsXML, title))
	return network.FetchWithOptions(ctx, ecfrURL, false, opts, nil)
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
