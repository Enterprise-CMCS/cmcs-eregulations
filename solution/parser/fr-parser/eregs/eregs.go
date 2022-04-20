package eregs

import (
	"strings"
	"net/url"
	"os"
	"fmt"
	"path"
	"context"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/network"

	log "github.com/sirupsen/logrus"
)

// BaseURL is the URL of the eRegs API
var BaseURL string

var DocumentURL = "/supplemental_content"

var postAuth = &network.PostAuth{
	Username: os.Getenv("EREGS_USERNAME"),
	Password: os.Getenv("EREGS_PASSWORD"),
}

type Section struct {
	Title string `json:"title"`
	Part string `json:"part"`
	Section string `json:"section_id"`
}

type FRDoc struct {
	Name string `json:"name"`
	Description string `json:"description"`
	Category string `json:"category"`
	URL string `json:"url"`
	Date string `json:"date"`
	DocketNumber string `json:"docket_number`
	Locations []*Section `json:"locations"`
}

func SendDocument(ctx context.Context, doc *FRDoc) error {
	eregsURL, err := url.Parse(BaseURL)
	if err != nil {
		return fmt.Errorf("Failed to parse eRegs URL \"%s\"", BaseURL)
	}
	eregsURL.Path = path.Join(eregsURL.Path, DocumentURL)
	code, err := network.SendJSON(ctx, eregsURL, doc, true, postAuth, network.HTTPPut)
	if err != nil {
		if code != -1 {
			return fmt.Errorf("Send failed with code %d: %+v", code, err)
		}
		return fmt.Errorf("Send failed: %+v", err)
	}
	return nil
}

func CreateSections(title string, s []string) []*Section {
	sections := make([]*Section, len(s))

	for i, section := range s {
		sp := strings.Split(section, ".")
		if len(sp) != 2 {
			log.Warn("[eregs] Section identifier ", section, " is invalid.")
			continue
		}

		sections[i] = &Section{
			Title: title,
			Part: sp[0],
			Section: sp[1],
		}
	}
	
	return sections
}
