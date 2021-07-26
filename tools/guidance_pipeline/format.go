package main

import (
	"path/filepath"
	"strings"
)

type Section struct {
	Title   string `json:"title"`
	Part    string `json:"part"`
	Section string `json:"section"`
}

func formatHeader(file string) string {
	header := filepath.Base(file)
	if strings.Contains(header, "-") {
		header = strings.Split(header, "- ")[1]
	}
	newHeader := strings.ReplaceAll(header, ".csv", "")
	return newHeader
}

func formatSections(sections []string) []Section {
	sectionSlice := make([]Section, 0)
	for _, section := range sections {
		if len(section) > 0 && len(section) < 10 { //Look into related final rule field in NPRMs
			removeSpace := strings.ReplaceAll(section, " ", "")
			partSection := strings.Split(removeSpace, ".")
			sec := Section{
				Title:   "42",
				Part:    partSection[0],
				Section: partSection[1],
			}
			sectionSlice = append(sectionSlice, sec)
		}
	}
	return sectionSlice
}

func formatFilename(outputDirectory string, reg string) string {
	return outputDirectory + "/" + reg + ".json"
}
