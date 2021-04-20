package parseXML

import (
	"encoding/xml"
	"errors"
	"fmt"
	"io"
	"log"
	"regexp"
	"strings"
)

type Part struct {
	XMLName   xml.Name     `xml:"DIV5"`
	Name      string       `xml:"N,attr"`
	Type      string       `xml:"TYPE,attr"`
	Header    string       `xml:"HEAD"`
	Authority string       `xml:"AUTH>PSPACE"`
	Source    string       `xml:"SOURCE>PSPACE"`
	Children  PartChildren `xml:",any"`
}

type Subpart struct {
	Header   string          `xml:"HEAD"`
	Name     string          `xml:"N,attr"`
	Type     string          `xml:"TYPE,attr"`
	Children SubpartChildren `xml:",any"`
}

type SubjectGroup struct {
	Header   string               `xml:"HEAD"`
	Name     string               `xml:"N,attr"`
	Type     string               `xml:"TYPE,attr"`
	Children SubjectGroupChildren `xml:",any"`
}

type Section struct {
	Type     string          `xml:"TYPE,attr"`
	Citation SectionCitation `xml:"N,attr"`
	Header   string          `xml:"HEAD"`
	Children SectionChildren `xml:",any"`
}

type PostProcesser interface {
	PostProcess(s *Section) error
}

type SectionCitation []string

func (sl *SectionCitation) UnmarshalText(data []byte) error {
	*sl = strings.Split(string(data), ".")
	return nil
}

func (s *Section) UnmarshalXML(d *xml.Decoder, start xml.StartElement) error {
	type postSection Section
	ps := (*postSection)(s)

	if err := d.DecodeElement(ps, &start); err != nil {
		return err
	}

	for _, child := range s.Children {
		c, ok := child.(PostProcesser)
		if ok {
			if err := c.PostProcess(s); err != nil && err != ErrNoParents {
				return err
			}
		}
	}
	return nil
}

// a, 1, roman, upper, italic int, italic roman
var alpha = regexp.MustCompile(`([a-z])`)
var num = regexp.MustCompile(`(\d+)`)
var roman = regexp.MustCompile(`(ix|iv|v|vi{1,3}|i{1,3})`)
var upper = regexp.MustCompile(`([A-Z])`)
var italic_num = regexp.MustCompile(`(<I>\d+</I>)`)
var italic_roman = regexp.MustCompile(`<I>(ix|iv|v|vi{1,3}|i{1,3})</I>`)

var paragraphHeirarchy = []*regexp.Regexp{
	alpha,
	num,
	roman,
	upper,
	italic_num,
	italic_roman,
}

func matchLabelType(l string) int {
	m := -1
	for i, reg := range paragraphHeirarchy {
		if reg.MatchString(l) {
			m = i
		}
	}
	return m
}

func firstParent(pLevel int, sibs []interface{}) []string {

	for _, unknownSib := range sibs {
		sib, ok := unknownSib.(*Paragraph)
		if !ok {
			continue
		}
		sibLabel, err := sib.Identifier()
		if err != nil {
			log.Println("[ERROR]", err)
			continue
		}

		for i, l := range sibLabel {
			subLevel := matchLabelType(l)

			if subLevel < pLevel {
				return sib.Citation[:len(sib.Citation)-(len(sibLabel)-(i+1))]
			}
		}
	}
	return nil
}

func extractSiblings(p *Paragraph, allChildren SectionChildren) ([]interface{}, error) {
	index := -1
	for i, c := range allChildren {
		if c == p {
			index = i
			break
		}
	}
	if index < 0 {
		return nil, fmt.Errorf("could not find paragraph in section")
	}
	sibs := []interface{}{}
	for _, c := range allChildren[:index] {
		sibs = append([]interface{}{c}, sibs...)
	}
	return sibs, nil
}

var ErrNoParents = errors.New("no parents found for this paragraph")

func (p *Paragraph) Identifier() ([]string, error) {
	// should handle cases of (a) or (a)(1)
	re := regexp.MustCompile(`^\(([^\)]+)(?:\)\(([^\)]+)+)?`)
	pLabel := re.FindStringSubmatch(p.Content)
	if len(pLabel) == 0 {
		return []string{}, nil
	}
	if len(pLabel) < 2 {
		return nil, fmt.Errorf("wrong number of labels")
	}
	if len(pLabel) == 3 && pLabel[2] == "" {
		pLabel = pLabel[:2]
	}
	pLabel = pLabel[1:]
	return pLabel, nil
}

func (p *Paragraph) PostProcess(s *Section) error {
	p.Citation = []string{}
	//p.Name = append([]string{}, s.Name...)
	pLabel, err := p.Identifier()
	if err != nil {
		return err
	}
	if len(pLabel) == 0 {
		return nil
	}

	pLevel := matchLabelType(pLabel[0])
	if pLevel == 0 {
		p.Citation = append(p.Citation, s.Citation...)
		p.Citation = append(p.Citation, pLabel...)
		log.Println("[DEBUG] top level paragraph", p.Citation)
		return nil
	}
	/*
		parse out the label in parens e.g. (a)
		parse out special cases of more than 1 e.g. (a)(1) or (a) some stuff in italics (1)
		edge case: no identifier, in this case we should be a hash or something e.g. definitions in 433.400
		find position in sections children (should be a quick compare)
		compute it's nested value e.g. a,1,i,A

		a
		b, 1
		b, 2
		b, 2, i

	*/
	sibs, err := extractSiblings(p, s.Children)
	if err != nil {
		return err
	}

	parent := firstParent(pLevel, sibs)

	if parent == nil {
		return ErrNoParents
	}

	p.Citation = append(p.Citation, parent...)
	p.Citation = append(p.Citation, pLabel...)

	return nil
}

type Paragraph struct {
	Parent   *Section
	Type     string
	Content  string `xml:",innerxml"`
	Citation []string
}

type Extract struct {
	Type    string
	Content string `xml:",innerxml"`
}

type Citation struct {
	Type    string
	Content string `xml:",innerxml"`
}

type Source struct {
	Type    string
	Header  string `xml:"HED"`
	Content string `xml:"PSPACE"`
}

type SectionAuthority struct {
	Type    string
	Content string `xml:",innerxml"`
}

type FlushParagraph struct {
	Type    string
	Content string `xml:",innerxml"`
}

type Image struct {
	Type   string
	Source string `xml:"src,attr"`
}

type PartChildren []interface{}
type SubpartChildren []interface{}
type SectionChildren []interface{}
type SubjectGroupChildren []interface{}

func (c *PartChildren) UnmarshalXML(d *xml.Decoder, start xml.StartElement) error {
	switch start.Name.Local {
	case "DIV6":
		child := &Subpart{}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	case "DIV8":
		child := &Section{}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	default:
		//return fmt.Errorf("Unknown XML type in Part: %+v", start)
		fmt.Printf("Unknown XML type in Part: %+v\n", start)
		d.Skip()
	}

	return nil
}

func (c *SubpartChildren) UnmarshalXML(d *xml.Decoder, start xml.StartElement) error {
	switch start.Name.Local {
	case "DIV8":
		child := &Section{}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	case "DIV7":
		child := &SubjectGroup{}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	case "SOURCE":
		child := &Source{Type: "Source"}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	default:
		//return fmt.Errorf("Unknown XML type in Subpart: %+v", start)
		fmt.Printf("Unknown XML type in Subpart: %+v\n", start)
		d.Skip()
	}
	return nil
}

func (c *SubjectGroupChildren) UnmarshalXML(d *xml.Decoder, start xml.StartElement) error {
	switch start.Name.Local {
	case "DIV8":
		child := &Section{}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	default:
		//return fmt.Errorf("Unknown XML type in Subpart: %+v", start)
		fmt.Printf("Unknown XML type in Subject Group: %+v\n", start)
		d.Skip()
	}
	return nil
}

func (c *SectionChildren) UnmarshalXML(d *xml.Decoder, start xml.StartElement) error {
	switch start.Name.Local {
	case "P":
		child := &Paragraph{Type: "Paragraph"}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	case "FP":
		child := &FlushParagraph{Type: "FlushParagraph"}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	case "img":
		child := &Image{Type: "Image"}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	case "EXTRACT":
		child := &Extract{Type: "Extract"}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	case "CITA":
		child := &Citation{Type: "Citation"}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	case "SECAUTH":
		child := &SectionAuthority{Type: "SectionAuthority"}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	default:
		//return fmt.Errorf("Unknown XML type in Section: %+v", start)
		fmt.Printf("Unknown XML type in Section: %+v\n", start)
		d.Skip()
	}

	return nil
}

func ParsePart(b io.ReadCloser) (*Part, error) {
	d := xml.NewDecoder(b)

	p := &Part{}
	log.Println("[DEBUG] Decoding part")
	if err := d.Decode(p); err != nil {
		return p, err
	}
	return p, nil
}
