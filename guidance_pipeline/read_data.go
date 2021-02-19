package main

import (
	"encoding/csv"
	"os"
)

func readData(file string) ([][]string, error) {

	guidanceFile, err := os.Open(file)

	if err != nil {
		return [][]string{}, err
	}
	defer guidanceFile.Close()

	reader := csv.NewReader(guidanceFile)

	// First line skip
	if _, err := reader.Read(); err != nil {
		return [][]string{}, err
	}

	records, err := reader.ReadAll()

	if err != nil {
		return [][]string{}, err
	}

	return records, nil
}
