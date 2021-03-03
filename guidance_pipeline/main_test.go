package main

import (
	"bytes"
	"flag"
	"io/ioutil"
	"os"
	"path/filepath"
	"testing"
)

var update = flag.Bool("update", false, "update .golden files")

func TestDataToJson(t *testing.T) {
	reg := "433-110"
	data := dataToJSON(reg)
	gp := filepath.Join("testdata", reg+".golden")

	if *update {
		t.Log("update golden file")
		if err := ioutil.WriteFile(gp, data, 0644); err != nil {
			t.Fatalf("failed to update golden file: %s", err)
		}
	}
	g, err := ioutil.ReadFile(gp)
	if err != nil {
		t.Fatalf("failed reading .golden: %s", err)
	}
	if !bytes.Equal(data, g) {
		t.Errorf("written json does not match .golden file")
	}
}

func dataToJSON(reg string) []byte {
	file := "testdata/final_rules.csv"
	header := formatHeader(file)
	f, _ := os.Open(file)
	records, _ := readData(f)

	regMap := makeMapOfRegs(header, records)

	dataJSON, _ := toJSON([]byte{}, header, regMap[reg])
	return dataJSON
}
