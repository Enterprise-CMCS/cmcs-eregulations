package main

import (
	"path/filepath"
	"strings"
)

func formatHeader(file string) string {
	header := filepath.Base(file)
	if strings.Contains(header, "-") {
		header = strings.Split(header, "- ")[1]
	}
	newHeader := strings.ReplaceAll(header, ".csv", "")
	return newHeader
}

func formatRegs(regs []string) []string {
	newRegs := make([]string, 0)
	for _, reg := range regs {
		if len(reg) > 0 {
			removeSpace := strings.ReplaceAll(reg, " ", "")
			newRegs = append(newRegs, strings.ReplaceAll(removeSpace, ".", "-"))
		}
	}
	return newRegs
}

func formatFilename(outputDirectory string, reg string) string {
	return outputDirectory + "/" + reg + ".json"
}
