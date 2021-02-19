package main

import (
	"encoding/json"
	"fmt"
)

type Link struct {
	Href string `json:"href"`
	Name string `json:"name"`
}

type Regulation struct {
	Header string `json:"header"`
	Links  Link `json:"links"`
	Regs   []string `json:"regs"`
}

func toJSON(guidances []Guidance) {

	var regulations []Regulation

	for _, guidance := range guidances {
		linkField := Link{
			Href: guidance.link,
			Name: guidance.name,
		}

		res := Regulation{
			Header: guidance.header,
			Links:  linkField,
			Regs:   guidance.regs,
		}

		regulations = append(regulations, res)
	}

	regsJSON, err := json.Marshal(regulations)
	if err != nil {
		fmt.Println("An error has occured :: ", err)
		return
	}

	fmt.Println(string(regsJSON))
}
