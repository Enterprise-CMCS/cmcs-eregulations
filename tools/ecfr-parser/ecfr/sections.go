package ecfr

type Part struct {
	Name     string    `json:"name"`
	Title    string    `json:"title"`
	Sections []Section `json:"section"`
	Subparts []Subpart `json:"subpart"`
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
		if child.Type == "section" {
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

	for _, section := range s.Children {
		sec := ExtractSection(title, section)
		sections = append(sections, sec)
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
