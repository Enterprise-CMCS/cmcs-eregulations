package main

import (
	"encoding/json"
)

// Regulation is a title and array of supplemental content
type Regulation struct {
	Title                string     `json:"title"`
	SupplementalContent []Guidance `json:"supplemental_content"`
}

func buildRegulation(title string, guidances []Guidance) Regulation {
	regulation := Regulation{
		Title:                title,
		SupplementalContent: guidances,
	}

	return regulation
}

func findReg(regulations []Regulation, reg Regulation) bool {
	for _, el := range regulations {
		if el.Title == reg.Title {
			return true
		}
	}
	return false
}

func toJSON(file []byte, title string, guidances []Guidance) ([]byte, error) {
	var regulations []Regulation

	if len(file) > 0 {
		err := json.Unmarshal(file, &regulations)
		if err != nil {
			return nil, err
		}
	}

	newReg := buildRegulation(title, guidances)
	if !findReg(regulations, newReg) {
		regulations = append(regulations, newReg)
	}

	regsJSON, err := json.MarshalIndent(regulations, "", " ")
	if err != nil {
		return nil, err
	}

	return regsJSON, nil
}
