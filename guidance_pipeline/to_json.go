package main

import (
	"encoding/json"
)

type Regulation struct {
	Header string     `json:"header"`
	Links  []Guidance `json:"links"`
}

func buildRegulation(header string, guidances []Guidance) Regulation {
	regulation := Regulation{
		Header: header,
		Links:  guidances,
	}

	return regulation
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
	regulations = append(regulations, newReg)

	regsJSON, err := json.MarshalIndent(regulations, "", " ")

	if err != nil {
		return nil, err
	}

	return regsJSON, nil
}
