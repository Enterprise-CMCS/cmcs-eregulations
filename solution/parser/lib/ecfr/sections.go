package ecfr

import "fmt"

// Section is the struct representing a section of a part
type Section struct {
	Title   string `json:"title"`
	Part    string `json:"part"`
	Section string `json:"section"`
}

// Subpart is the struct representing a subpart of a part
type Subpart struct {
	Title    string    `json:"title"`
	Part     string    `json:"part"`
	Subpart  string    `json:"subpart"`
	Sections []Section `json:"sections"`
}

// ExtractStructure is a function to extract the sections and subparts from an eCFR structure
func ExtractStructure(s Structure, depth int) ([]Section, []Subpart, error) {
	if len(s.Identifier) < 1 {
		return nil, nil, fmt.Errorf("part identifier not found")
	}

	title := s.Identifier[0]

	structureChildren := s.Children
	var structurePart *Structure
	for i := 0; i != depth; i++ {
		if len(structureChildren) < 1 {
			return nil, nil, fmt.Errorf("structure does not match depth of %d", depth)
		}
		structurePart = structureChildren[0]
		structureChildren = structurePart.Children
	}

	partNumber := structurePart.Identifier[0]
	sections := []Section{}
	subparts := []Subpart{}

	for _, child := range structurePart.Children {
		if child.Type == "section" && !child.Reserved {
			sec := extractSection(title, child)
			sections = append(sections, sec)
		} else if child.Type == "subpart" {
			subp := extractSubpart(title, partNumber, child)
			subparts = append(subparts, subp)
		}
	}

	return sections, subparts, nil
}

func extractSubpart(title string, partNumber string, s *Structure) Subpart {
	sections := []Section{}

	for _, child := range s.Children {
		if !child.Reserved {
			if child.Type == "section" {
				sec := extractSection(title, child)
				sections = append(sections, sec)
			} else if child.Type == "subject_group" {
				for _, subChild := range child.Children {
					if subChild.Type == "section" && !subChild.Reserved {
						subSec := extractSection(title, subChild)
						sections = append(sections, subSec)
					}
				}
			}
		}
	}

	subpart := Subpart{
		Title:    title,
		Part:     partNumber,
		Subpart:  s.Identifier[0],
		Sections: sections,
	}

	return subpart
}

func extractSection(title string, s *Structure) Section {
	section := Section{
		Title:   title,
		Part:    s.Identifier[0],
		Section: s.Identifier[1],
	}

	return section
}
