package main

import (
	"encoding/json"
)

type Regulation struct {
	Header string     `json:"title"`
	Links  []Guidance `json:"supplementary_content"`
}

func buildRegulation(header string, guidances []Guidance) Regulation {
	regulation := Regulation{
		Header: header,
		Links:  guidances,
	}

	return regulation
}

func findReg(regulations []Regulation, reg Regulation) bool {
	for _, el := range regulations {
		if el.Header == reg.Header {
			return true
		}
	}
	return false
}

func toJSON(file []byte, header string, guidances []Guidance) ([]byte, error) {
	var regulations []Regulation

	if len(file) > 0 {
		err := json.Unmarshal(file, &regulations)
		if err != nil {
			return nil, err
		}
	}

	newReg := buildRegulation(header, guidances)
	if !findReg(regulations, newReg) {
		regulations = append(regulations, newReg)
	}

	regsJSON, err := json.MarshalIndent(regulations, "", " ")
	if err != nil {
		return nil, err
	}

	return regsJSON, nil
}
