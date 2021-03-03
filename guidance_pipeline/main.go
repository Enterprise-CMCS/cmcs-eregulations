package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"
)

type Guidance struct {
	Name string   `json:"name"`
	Link string   `json:"href"`
	Regs []string `json:"regs"`
}

func main() {
	if len(os.Args) != 2 {
		fmt.Println("Usage:", "./guidance", "FILE")
		return
	}

	file := os.Args[1]
	header := formatHeader(file)

	f, err := os.Open(file)
	if err != nil {
		log.Fatal("An error has occured :: ", err)
	}
	defer f.Close()

	records, err := readData(f)

	if err != nil {
		log.Fatal("An error has occured :: ", err)
		return
	}

	regMap := makeMapOfRegs(header, records)

	if err := writeRegsToFile(header, regMap); err != nil {
		log.Fatal("An error has occured :: ", err)
	}
}

func makeMapOfRegs(header string, records [][]string) map[string][]Guidance {
	regMap := make(map[string][]Guidance)

	for _, record := range records {
		if len(record[0]) > 0 {
			regs := formatRegs(record[2:])

			for _, reg := range regs {
				guidance := Guidance{
					Name: record[0],
					Link: record[1],
					Regs: regs,
				}

				regMap[reg] = append(regMap[reg], guidance)
			}
		}
	}
	return regMap
}

func writeRegsToFile(header string, regs map[string][]Guidance) error {
	for key, reg := range regs {
		filename := formatFilename(key)
		f, err := ioutil.ReadFile(filename)
		dataJSON, err := toJSON(f, header, reg)
		if err != nil {
			return err
		}
		file, err := os.OpenFile(filename, os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			return err
		}
		defer file.Close()
		if err := writeData(file, dataJSON); err != nil {
			return err
		}
	}

	return nil
}
