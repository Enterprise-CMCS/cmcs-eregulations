package main

import (
	"encoding/csv"
	"io"
)

func readData(file io.Reader) ([][]string, error) {
	reader := csv.NewReader(file)

	// First line skip
	if _, err := reader.Read(); err != nil {
		return nil, err
	}

	records, err := reader.ReadAll()

	if err != nil {
		return nil, err
	}

	return records, nil
}
