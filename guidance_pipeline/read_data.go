package main

import (
	"bufio"
	"encoding/csv"
	"io"
)

func readCSV(file io.Reader) ([][]string, error) {
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

func readFile(file io.Reader)([]string, error) {
	var lines []string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		lines = append(lines, scanner.Text())
	}
	return lines, scanner.Err()
} 