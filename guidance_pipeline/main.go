package main

import (
	"fmt"
	"os"
)

type Guidance struct {
	header string
	name   string
	link   string
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

	for _, record := range records {
		regs := record[2:]
		guidance := Guidance{
			// for now header is the filename change this
			header: "Final",
			name:   record[0],
			link:   record[1],
		}

		fmt.Printf("header: %s\n name: %s\n href: %s\n regs: %s\n", guidance.header, guidance.name, guidance.link, regs)
	}
}
