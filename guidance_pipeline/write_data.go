package main

import (
	"fmt"
	"os"
)

func writeData(filename string, data []byte) {
	f, err := os.OpenFile(filename, os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		fmt.Println("An error has occured :: ", err)
	}
	if _, err := f.Write(data); err != nil {
		fmt.Println("An error has occured :: ", err)
	}
	if err := f.Close(); err != nil {
		fmt.Println("An error has occured :: ", err)
	}
}
