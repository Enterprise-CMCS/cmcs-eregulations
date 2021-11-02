package ecfr

import (
	"regexp"
)

type Section struct {
	Title   string `json:"title"`
	Part    string `json:"part"`
	Section string `json:"section"`
}

type Subpart struct {
	Title   string `json:"title"`
	Part    string `json:"part"`
	Subpart string `json:"subpart"`
}

func ExtractStructure(s Structure) {
	title := ExtractTitle(s)
	part := s.Children[0].Children[0].Children
	partNumber := part[0].Identifier[0]
	for _, child := range part[0].Children {
		if child.Type == "section" {
			ExtractSection(title, child)
		} else if child.Type == "subpart" {
			ExtractSubpart(title, partNumber, child)

			for _, section := range child.Children {
				ExtractSection(title, section)
			}
		}
	}
}

func ExtractTitle(s Structure) string {
	re := regexp.MustCompile("[0-9]+")
	if s.Type == "title" {
		title := re.FindString(s.Label)
		return title
	} else {
		// probably needs to be an error
		return ""
	}
}

func ExtractSubpart(title string, partNumber string, s *Structure) Subpart {
	subpart := Subpart{
		Title:   title,
		Part:    partNumber,
		Subpart: s.Identifier[0],
	}

	return subpart
}

func ExtractSection(title string, s *Structure) Section {
	section := Section{
		Title:   title,
		Part:    s.Identifier[0],
		Section: s.Identifier[1],
	}

	return section
}
