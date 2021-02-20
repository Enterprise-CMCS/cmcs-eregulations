package main

import (
	"io/ioutil"
)

func writeData(fileName string, data []byte) {
	filePath := "guidance/" + fileName + ".json"
	_ = ioutil.WriteFile(filePath, data, 0644)
}