package ecfr

type Structure struct {
	Identifier       string
	Label            string
	LabelLevel       string `json:"label_level"`
	LabelDescription string `json:"label_discription"`
	Reserved         bool
	Type             string
	Children         []*Structure
}

func SubchapterParts(s *Structure) []*Structure {
	return s.Children[0].Children[0].Children
}
