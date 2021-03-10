package main

import (
	"errors"
	"io"
	"mime"
	"net/http"
)

func downloadCSV(url string) (string, io.ReadCloser, error) {
	resp, err := http.Get(url)
	if err != nil {
		return "", nil, err
	}
	content := resp.Header.Get("Content-Disposition")
	_, params, err := mime.ParseMediaType(content)
	if err != nil {
		return "", nil, err
	}
	header := params["filename"]

	if resp.StatusCode != 200 {
		return "", nil, errors.New("Received non 200 response code")
	}

	return header, resp.Body, nil
}