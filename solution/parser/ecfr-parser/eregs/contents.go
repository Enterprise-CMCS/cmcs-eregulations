package eregs

import (
	"fmt"
	"sort"
	"strings"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
)

// Title represents a title object from eRegs, specifically for table of contents processing
type Title struct {
	Name string `json:"name"`
	Contents *ecfr.Structure `json:"toc"`
	Exists bool
	Modified bool
}

// AddPart adds a part to a title if it's not already there, otherwise updates it
func (t *Title) AddPart(s *ecfr.Structure, part string) {
	addPart(t.Contents, s, part)
}

func identifierStringEqual(one *ecfr.IdentifierString, two *ecfr.IdentifierString) bool {
	if len(*one) != len(*two) {
		return false
	}
	for i := range *one {
		if (*one)[i] != (*two)[i] {
			return false
		}
	}
	return true
}

func copyStructure(src *ecfr.Structure) *ecfr.Structure {
	return &ecfr.Structure{
		Identifier: src.Identifier,
		Label: src.Label,
		LabelLevel: src.LabelLevel,
		LabelDescription: src.LabelDescription,
		Reserved: src.Reserved,
		Type: src.Type,
		DescendantRange: src.DescendantRange,
		Children: []*ecfr.Structure{},
	}
}

func addPart(dest *ecfr.Structure, src *ecfr.Structure, part string) {
	if len(dest.Identifier) == 0 {
		//dest structure is empty, populate it (should only occur on first creation of a title)
		*dest = *(copyStructure(src))
	}

	//return if src node is a part or has no children
	if len(src.Children) == 0 || src.Type == "part" {
		return
	}

	//determine if first child of src exists in dest subtree
	index := -1
	for i, destChild := range dest.Children {
		if identifierStringEqual(&src.Children[0].Identifier, &destChild.Identifier) {
			index = i
		}
	}

	if index == -1 {
		//first child of src does not exist, add it
		dest.Children = append(dest.Children, copyStructure(src.Children[0]))
		if src.Children[0].Type != "part" || src.Children[0].Identifier[0] != part {
			//not the part we're looking for, so recurse down a level
			addPart(dest.Children[len(dest.Children)-1], src.Children[0], part)
		}
		sort.Slice(dest.Children, func(i, j int) bool { //sort children alphabetically
			return strings.Join(dest.Children[i].Identifier, " ") < strings.Join(dest.Children[j].Identifier, " ")
		})
	} else if src.Children[0].Type == "part" && src.Children[0].Identifier[0] == part {
		//this is the part we're looking for, and it already exists, so update it
		dest.Children[index] = copyStructure(src.Children[0])
	} else {
		//not the part we're looking for but does exist, so recurse down a level
		addPart(dest.Children[index], src.Children[0], part)
	}
}

// RemovePart removes a part from a title if it exists
func (t *Title) RemovePart(part string) error {
	if !removePart(&t.Contents.Children, part) {
		return fmt.Errorf("Part %s not found and not removed", part)
	}
	return nil
}

func removePart(s *[]*ecfr.Structure, p string) bool {
	//determine if part exists within current subtree
	index := -1
	for i, child := range *s {
		if child.Type == "part" && child.Identifier[0] == p {
			index = i
		}
	}

	if index != -1 {
		//it does, remove it and return true
		*s = append((*s)[:index], (*s)[index+1:]...)
		return true
	}

	//it doesn't, recurse into lower subtrees
	for i, child := range *s {
		if removePart(&child.Children, p) {
			if len(child.Children) == 0 && child.Type != "part" {
				//this subtree is not a part and is now empty, remove it
				*s = append((*s)[:i], (*s)[i+1:]...)
			}
			return true
		}
	}

	//part doesn't exist anywhere in this subtree
	return false
}
