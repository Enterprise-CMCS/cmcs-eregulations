package ecfr

type Part struct {
	Name     string    `json:"name"`
	Title    string    `json:"title"`
	Sections []Section `json:"sections"`
	Subparts []Subpart `json:"subparts"`
}

type Section struct {
	Title   string `json:"title"`
	Part    string `json:"part"`
	Section string `json:"section"`
}

type Subpart struct {
	Title    string    `json:"title"`
	Part     string    `json:"part"`
	Subpart  string    `json:"subpart"`
	Sections []Section `json:"sections"`
}

func ExtractStructure(s Structure) (Part, error) {
	title := s.Identifier[0]
	structurePart := s.Children[0].Children[0].Children
	partNumber := structurePart[0].Identifier[0]
	sections := []Section{}
	subparts := []Subpart{}

	for _, child := range structurePart[0].Children {
		if child.Type == "section" && !child.Reserved {
			sec := ExtractSection(title, child)
			sections = append(sections, sec)
		} else if child.Type == "subpart" {
			subp := ExtractSubpart(title, partNumber, child)
			subparts = append(subparts, subp)
		}
	}

	p := Part{
		Name:     partNumber,
		Title:    title,
		Sections: sections,
		Subparts: subparts,
	}

	return p, nil
}

func ExtractSubpart(title string, partNumber string, s *Structure) Subpart {
	sections := []Section{}

	for _, child := range s.Children {
		if !child.Reserved {
			if child.Type == "section" {
				sec := ExtractSection(title, child)
				sections = append(sections, sec)
			} else if child.Type == "subject_group" {
				for _, subChild := range child.Children {
					if subChild.Type == "section" && !subChild.Reserved {
						subSec := ExtractSection(title, subChild)
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

func ExtractSection(title string, s *Structure) Section {
	section := Section{
		Title:   title,
		Part:    s.Identifier[0],
		Section: s.Identifier[1],
	}

	return section
}
