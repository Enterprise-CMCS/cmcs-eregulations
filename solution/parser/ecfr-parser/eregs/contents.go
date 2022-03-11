package eregs

import (
	"fmt"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
)

type Title struct {
	Name string `json:"name"`
	Contents *ecfr.Structure `json:"toc"`
}

// AddPart adds a part to a title if it's not already there, otherwise updates it
func (t *Title) AddPart(part *Part) error {
	return nil
}

func addPart(s *ecfr.Structure, part *Part) bool {
	return false
}

// RemovePart removes a part from a title if it exists
func (t *Title) RemovePart(part string) error {
	if !removePart(&t.Contents.Children, part) {
		return fmt.Errorf("Part not found and not removed")
	}
	return nil
}

func removePart(s *[]*ecfr.Structure, p string) bool {
	//determine if part exists within current children list
	index := -1
	for i, child := range *s {
		if child.Type == "part" && child.Identifier[0] == p {
			index = i
		}
	}

	//it does, remove it and return true
	if index != -1 {
		*s = append((*s)[:index], (*s)[index+1:]...)
		return true
	}

	//it doesn't, recurse into children lists
	for i, child := range *s {
		if removePart(&child.Children, p) {
			if len(child.Children) == 0 && child.Type != "part" {
				//this subtree is not a part and is now empty, remove it
				*s = append((*s)[:i], (*s)[i+1:]...)
			}
			return true
		}
	}

	//part doesn't exist anywhere
	return false
}
