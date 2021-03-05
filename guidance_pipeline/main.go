package main

import (
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
)

type Guidance struct {
	Name string   `json:"name"`
	Link string   `json:"href"`
	Regs []string `json:"regs"`
}

var file = flag.String("f", "", "supply a file of URLs to download")
var directory = flag.String("d", "", "give a directory to read from")
var outputDirectory = flag.String("o", "guidance", "give the directory you want to output the files to.")

func main() {
	flag.Usage = func(){
		fmt.Fprintf(os.Stderr, "Usage: %s [options] [file]\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()
	if len(os.Args) < 2 {
		fmt.Fprintf(os.Stderr, "Usage: %s [options] [file]\n", os.Args[0])
		flag.PrintDefaults()
		return
	}

	if(len(*directory) > 0) {
		files, err := ioutil.ReadDir(*directory)
		if err != nil {
			log.Fatal(err)
		}

		for _, file := range files {
			if(filepath.Ext(file.Name()) == ".csv") {
				path := filepath.Join(*directory, file.Name())
				processDataFromFile(path)
			}
		}
	} else if (filepath.Ext(*file) == ".txt") {
		f, err := os.Open(*file)
		if err != nil {
			log.Fatal("An error has occured :: ", err)
		}
		urls, err := readFile(f)
		if err != nil {
			log.Fatal("An error has occured :: ", err)
		}
		fmt.Println(urls)
	} else {
		processDataFromFile(*file)
	}
}

func processDataFromFile(file string) {
	header := formatHeader(file)

	f, err := os.Open(file)
	if err != nil {
		log.Fatal("An error has occured :: ", err)
	}
	defer f.Close()

	records, err := readCSV(f)

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
		filename := formatFilename(*outputDirectory, key)
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
