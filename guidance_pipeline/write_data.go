package main

import (
	"log"
	"os"
)

func writeData(filename string, data []byte) {
	f, err := os.OpenFile(filename, os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatal("An error has occured :: ", err)
	}
	if _, err := f.Write(data); err != nil {
		log.Fatal("An error has occured :: ", err)
	}
	if err := f.Close(); err != nil {
		log.Fatal("An error has occured :: ", err)
	}
}
