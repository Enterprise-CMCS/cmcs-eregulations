package main

import (
	"path/filepath"
	"strings"
)

func formatHeader(file string) string {
	header := filepath.Base(file)
	splitHeader := strings.Split(header, "- ")
	newHeader := strings.ReplaceAll(splitHeader[1], ".csv", "")
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

func formatFilename(reg string) string {
	return "guidance/" + reg + ".json"
}
