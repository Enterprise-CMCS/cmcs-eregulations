package fedreg

import (
	"context"
	"net/url"
	"fmt"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/network"
)

var FedRegURL= "https://www.federalregister.gov/api/v1/documents.json?fields[]=type&fields[]=abstract&fields[]=citation&fields[]=correction_of&fields[]=action&fields[]=dates&fields[]=docket_id&fields[]=docket_ids&fields[]=document_number&fields[]=effective_on&fields[]=html_url&fields[]=publication_date&fields[]=regulation_id_number_info&fields[]=regulation_id_numbers&fields[]=title&order=newest&conditions[cfr][title]=%d&conditions[cfr][part]=%d"

func FetchContent(ctx context.Context, title int, part int) (X, int, error) {
	path := fmt.Sprintf(FedRegURL, title, part)
	fedregURL, err := url.Parse(path)
	if err != nil {
		return nil, -1, err
	}
	return network.Fetch(ctx, fedregURL, false)
}
