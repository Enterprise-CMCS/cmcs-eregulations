package main

import (
	"flag"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/url"
	"os"
	"path/filepath"
)

type Guidance struct {
	Title    string    `json:"title"`
	Url      string    `json:"url"`
	Sections []Section `json:"sections"`
}

var file = flag.String("f", "", "supply a file of URLs to download or a csv file")
var directory = flag.String("d", "", "give a directory of csv files")
var csvURL = flag.String("u", "", "give a url to a csv file")
var outputDirectory = flag.String("o", "guidance", "give the directory with which you want to output json")

func main() {
	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s [options] [file]\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()
	flags := make(map[string]bool)
	flag.Visit(func(f *flag.Flag) { flags[f.Name] = true })
	if !(flags["f"] || flags["d"] || flags["u"]) {
		flag.Usage()
		return
	}

	logFile, err := os.OpenFile("logs.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0666)
	if err != nil {
		log.Fatal(err)
	}
	defer logFile.Close()
	mw := io.MultiWriter(os.Stderr, logFile)
	log.SetOutput(mw)

	if len(*directory) > 0 {
		processDirectory(*directory)
	} else if filepath.Ext(*file) == ".txt" {
		processURLsFromFile(*file)
	} else if len(*csvURL) > 0 {
		processURL(*csvURL)
	} else {
		processFile(*file)
	}
}

func processDirectory(directory string) {
	files, err := ioutil.ReadDir(directory)
	if err != nil {
		log.Fatal(err)
	}

	for _, file := range files {
		if filepath.Ext(file.Name()) == ".csv" {
			path := filepath.Join(directory, file.Name())
			processFile(path)
		}
	}
}

func processURLsFromFile(file string) {
	f, err := os.Open(file)
	if err != nil {
		log.Fatal("An error has occured :: ", err)
	}
	urls, err := readFile(f)
	if err != nil {
		log.Fatal("An error has occured :: ", err)
	}
	for _, u := range urls {
		processURL(u)
	}
}

func processURL(csvURL string) {
	header, body, err := downloadCSV(csvURL)
	if err != nil {
		log.Fatal("An error has occured :: ", err)
	}
	defer body.Close()
	processData(formatHeader(header), body)
}

func processFile(file string) {
	header := formatHeader(file)

	f, err := os.Open(file)
	if err != nil {
		log.Fatal("An error has occured :: ", err)
	}
	defer f.Close()
	processData(header, f)
}

func processData(header string, data io.Reader) {
	records, err := readCSV(data)

	if err != nil {
		log.Fatal("An error has occured :: ", err)
		return
	}

	regMap := makeMapOfRegs(header, records)

	if err := writeRegsToFile(header, regMap); err != nil {
		log.Fatal("An error has occured :: ", err)
	}
}

func validURL(header string, link string) (string, error) {
	_, err := url.ParseRequestURI(link)
	if err != nil {
		err := fmt.Errorf("%s %s", header, err)
		return "", err
	}
	return link, nil
}

func makeMapOfRegs(header string, records [][]string) map[string][]Guidance {
	regMap := make(map[string][]Guidance)

	for _, record := range records {
		if len(record[0]) > 0 {
			link, err := validURL(header, record[1])
			if err != nil {
				log.Println(err)
				continue
			}
			sections := formatSections(record[2:])

			for _, section := range sections {
				guidance := Guidance{
					Title:    record[0],
					Url:      link,
					Sections: sections,
				}
				sectionString := section.Part + "-" + section.Section
				regMap[sectionString] = append(regMap[sectionString], guidance)
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
			err := fmt.Errorf("%s %s", filename, err)
			return err
		}
		defer file.Close()
		if err := writeData(file, dataJSON); err != nil {
			err := fmt.Errorf("%s %s", filename, err)
			return err
		}
	}

	return nil
}
