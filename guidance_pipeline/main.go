package main

import (
	"fmt"
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
	records, err := readData(file)

	if err != nil {
		fmt.Println("An error has occured :: ", err)
		return
	}

	var guidances []Guidance 

	for _, record := range records {
		guidance := Guidance{
			// for now header is the filename change this
			header: "Final",
			name:   record[0],
			link:   record[1],
			regs:   record[2:],
		}

		guidances = append(guidances, guidance)
	}

	toJSON(guidances)
}