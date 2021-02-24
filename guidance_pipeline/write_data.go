package main

import (
	"io/ioutil"
	"os"
)

func writeData(filename string, data []byte) {
	_ = ioutil.WriteFile(filename, data, 0644)
}

func checkFile(filename string) error {
	_, err := os.Stat(filename)

	if os.IsNotExist(err) {
		_, err := os.Create(filename)
		if err != nil {
			return err
		}
	}
	return nil
}
