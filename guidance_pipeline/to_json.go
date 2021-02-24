package main

import (
	"encoding/json"
	"fmt"
)

type Link struct {
	Href string   `json:"href"`
	Name string   `json:"name"`
	Regs []string `json:"regs"`
}

type Regulation struct {
	Header string `json:"header"`
	Links  []Link `json:"links"`
}

func toJSON(header string, guidances []Guidance) ([]byte, error) {

	links := make([]Link, 0)
	for _, guidance := range guidances {
		linkField := Link{
			Href: guidance.link,
			Name: guidance.name,
			Regs: guidance.regs,
		}
		links = append(links, linkField)
	}

	regulation := Regulation{
		Header: header,
		Links:  links,
	}

	regsJSON, err := json.MarshalIndent(regulation, "", " ")
	if err != nil {
		fmt.Println("An error has occured :: ", err)
		return []byte{}, err
	}

	return regsJSON, nil
}
