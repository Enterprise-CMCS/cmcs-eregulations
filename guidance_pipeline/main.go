package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

type Guidance struct {
	header string
	name   string
	link   string
	regs   []string
}

func main() {
	if len(os.Args) != 2 {
		fmt.Println("Usage:", "./guidance", "FILE")
		return
	}

	file := os.Args[1]
	header := filepath.Base(file)
	records, err := readData(file)

	if err != nil {
		fmt.Println("An error has occured :: ", err)
		return
	}

	var guidances []Guidance 

	for _, record := range records {
		if(len(record[0]) > 0) {
			guidance := Guidance{
				header: header,
				name:   record[0],
				link:   record[1],
				regs:   formatRegs(record[2:]),
			}

			guidances = append(guidances, guidance)
		}
	}

	dataJSON, err := toJSON(guidances)

	if err != nil {
		fmt.Println("An error has occured :: ", err)
		return
	}

	fmt.Println(string(dataJSON))
}

func formatRegs(regs []string) []string {
	newRegs := make([]string, 0)
	for _, reg := range regs {
		if len(reg) > 0 {
			newRegs = append(newRegs, strings.ReplaceAll(reg, ".", "-"))
		} 
	}
	return newRegs
}