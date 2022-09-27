package api

import (
	"context"
	"net/url"
	"path"
	"io"
	"os"
	
	"github.com/cmsgov/cmcs-eregulations/network"
)

// BaseURL is the URL of the eRegs service that will accept the post requests
var BaseURL string

var postAuth = &network.PostAuth{
	Username: os.Getenv("EREGS_USERNAME"),
	Password: os.Getenv("EREGS_PASSWORD"),
}

func Get(ctx context.Context, apiPath string) (io.Reader, int, error) {
	u, err := parseURL(apiPath)
	if err != nil {
		return nil, -1, err
	}
	body, code, err := network.Fetch(ctx, u, true)
	if err != nil {
		return nil, code, err
	}
	return body, code, nil
}

func Post(ctx context.Context, apiPath string, data interface{}) (int, error) {
	return upload(ctx, apiPath, data, network.HTTPPost)
}

func Put(ctx context.Context, apiPath string, data interface{}) (int, error) {
	return upload(ctx, apiPath, data, network.HTTPPut)
}

func upload(ctx context.Context, apiPath string, data interface{}, method string) (int, error) {
	u, err := parseURL(apiPath)
	if err != nil {
		return -1, err
	}
	return network.SendJSON(ctx, u, data, true, postAuth, method)
}

func parseURL(apiPath string) (*url.URL, error) {
	u, err := url.Parse(BaseURL)
	if err != nil {
		return nil, err
	}
	u.Path = path.Join(u.Path, apiPath)
	return u, nil
}
