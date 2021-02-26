package main

import (
	"fmt"
	"io/ioutil"
	"os"
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
	header := formatHeader(file)
	records, err := readData(file)

	if err != nil {
		fmt.Println("An error has occured :: ", err)
		return
	}

	// create a map for guidances
	regMap := make(map[string][]Guidance)

	for _, record := range records {
		if len(record[0]) > 0 {
			regs := formatRegs(record[2:])

			for _, reg := range regs {
				guidance := Guidance{
					header: header,
					name:   record[0],
					link:   record[1],
					regs:   regs,
				}

				regMap[reg] = append(regMap[reg], guidance)
			}
		}
	}

	// Write regs to file
	for key, reg := range regMap {
		filename := formatFilename(key)
		f, err := ioutil.ReadFile(filename)
		dataJSON, err := toJSON(f, header, reg)
		if err != nil {
			fmt.Println("An error has occured :: ", err)
			return
		}
		writeData(filename, dataJSON)
	}
}
