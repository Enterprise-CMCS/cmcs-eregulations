package eregs

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"os"
	"path"
	"strings"
	"time"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/parsexml"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/network"

	log "github.com/sirupsen/logrus"
)

// BaseURL is the URL of the eRegs service that will accept the post requests
var BaseURL string

var client = &http.Client{
	Transport: &http.Transport{},
}

var partURL  = "/title/%d/existing"

var postAuth = &network.PostAuth{
	Username: os.Getenv("EREGS_USERNAME"),
	Password: os.Getenv("EREGS_PASSWORD"),
}

// Part is the struct used to send a part to the eRegs server
type Part struct {
	Title     	   int             `json:"title,string" xml:"-"`
	Name      	   string          `json:"name" xml:"-"`
	Date      	   string          `json:"date" xml:"-"`
	Structure 	   *ecfr.Structure `json:"structure" xml:"-"`
	Document  	   *parsexml.Part  `json:"document"`
	Depth	  	   int			   `json:"depth"`
	Processed 	   bool
	UploadContents bool
}

// ExistingPart is a regulation that has been loaded already
type ExistingPart struct {
	Date     string   `json:"date"`
	PartName []string `json:"partName"`
}

// ParserResult is the struct used to send results to the eRegs server
type ParserResult struct {
	Title     	        int             `json:"title,string"`
	Start      	        string          `json:"start,date"`
	End      	        string          `json:"end,date"`
    Workers             int             `json:"workers,string"`
    Attempts            int             `json:"attempts,string"`
    Parts               string          `json:"parts"`
    Subchapters         string          `json:"subchapters"`
    SkippedVersions     int             `json:"skippedVersions,string"`
    TotalVersions       int             `json:"totalVersions,string"`
    Errors              int             `json:"errors,string"`
}

// PostPart is the function that sends a part to the eRegs server
func PostPart(ctx context.Context, p *Part) (int, error) {
	eregsPath, err := url.Parse(BaseURL)
	if err != nil {
		return -1, err
	}
	return network.SendJSON(ctx, eregsPath, p, true, postAuth, network.HTTPPost)
}

// PostSupplementalPart is the function that sends a supplemental part to eRegs server
func PostSupplementalPart(ctx context.Context, p ecfr.Part) (int, error) {
	eregsPath, err := url.Parse(BaseURL)
	if err != nil {
		return -1, err
	}
	eregsPath.Path = path.Join(eregsPath.Path, "/supplemental_content")
	return network.SendJSON(ctx, eregsPath, p, true, postAuth, network.HTTPPost)
}

// PostParserResult is the function that sends a parser result to the eRegs server
func PostParserResult(ctx context.Context, p *ParserResult) (int, error) {
	eregsPath, err := getV3URL()
	if err != nil {
		return -1, err
	}

	eregsPath.Path = path.Join(eregsPath.Path, fmt.Sprintf( "/ecfr_parser_result/%d", p.Title))
	p.End = time.Now().Format(time.RFC3339)
	return network.SendJSON(ctx, eregsPath, p, true, postAuth, network.HTTPPost)
}

// GetTitle retrieves a title object from regcore in eRegs
func GetTitle(ctx context.Context, title int) (*Title, int, error) {
	emptyTitle := &Title{
		Name: fmt.Sprintf("%d", title),
		Contents: &ecfr.Structure{},
		Exists: false,
		Modified: false,
	}

	eregsPath, err := getV3URL()
	if err != nil {
		return emptyTitle, -1, err
	}
	eregsPath.Path = path.Join(eregsPath.Path, fmt.Sprintf("/title/%d", title))
	
	log.Trace("[eregs] Retrieving title ", title, " from eRegs")

	body, code, err := network.Fetch(ctx, eregsPath, true)
	if err != nil {
		return emptyTitle, code, err
	}

	var t Title
	d := json.NewDecoder(body)
	if err := d.Decode(&t); err != nil {
		return emptyTitle, code, fmt.Errorf("Unable to decode response body while retrieving title object: %+v", err)
	}
	
	t.Exists = true
	t.Modified = false

	return &t, code, nil
}

// SendTitle sends a title object to regcore in eRegs for table of contents tracking
func SendTitle(ctx context.Context, t *Title) (int, error) {
	eregsPath, err := getV3URL()
	if err != nil {
		return -1, nil
	}
	eregsPath.Path = path.Join(eregsPath.Path, fmt.Sprintf("/title/%s", t.Name))
	var method string
	if t.Exists {
		method = network.HTTPPut
	} else {
		method = network.HTTPPost
	}
	return network.SendJSON(ctx, eregsPath, t, true, postAuth, method)
}

// GetExistingParts gets existing parts already imported
func GetExistingParts(ctx context.Context, title int) (map[string][]string, int, error) {
	checkURL, err := url.Parse(BaseURL)
	if err != nil {
		return nil, -1, err
	}
	checkURL.Path = path.Join(checkURL.Path, fmt.Sprintf(partURL, title))

	log.Trace("[eregs] Beginning checking of existing parts for title ", title, " at ", checkURL.String())

	body, code, err := network.Fetch(ctx, checkURL, true)
	if err != nil {
		return nil, code, err
	}

	// Cast the body to an array of existing parts
	var vs []ExistingPart
	d := json.NewDecoder(body)
	if err := d.Decode(&vs); err != nil {
		return nil, code, fmt.Errorf("Unable to decode response body while checking existing versions: %+v", err)
	}

	// reduce the results to the desired format
	result := make(map[string][]string)
	for _, ep := range vs {
		result[ep.Date] = ep.PartName
	}

	return result, code, nil
}

func getV3URL() (*url.URL, error){
    eregsPath, err := url.Parse(BaseURL)
    if err != nil {
        log.Fatal(err)
        return nil, err
    }
	if strings.HasSuffix(eregsPath.Path, "v2/") {
		eregsPath.Path = eregsPath.Path[0:len(eregsPath.Path)-3] + "v3" // very bad!
	}
	return eregsPath, nil
}