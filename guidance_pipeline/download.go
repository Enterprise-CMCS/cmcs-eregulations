package main

import (
	"errors"
	"io"
	"net/http"
)

func downloadCSV(url string) (io.ReadCloser, error) {
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	// defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return nil, errors.New("Received non 200 response code")
	}

	return resp.Body, nil
}