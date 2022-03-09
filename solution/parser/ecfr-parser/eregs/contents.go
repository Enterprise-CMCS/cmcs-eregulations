package eregs

import (
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
)

type Title struct {
	Name string `json:"name"`
	Contents *ecfr.Structure `json:"toc"`
}

func UpdateTitle()
