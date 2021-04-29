package parseXML

import (
	"crypto/md5"
	"encoding/xml"
	"errors"
	"fmt"
	"io"
	"log"
	"strings"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
)

type PostProcesser interface {
	PostProcess() error
}

func ParsePart(b io.Reader) (*Part, error) {
	d := xml.NewDecoder(b)

	p := &Part{}
	if err := d.Decode(p); err != nil {
		return p, err
	}
	return p, nil
}

type Part struct {
	XMLName   xml.Name        `xml:"DIV5" json:"-"`
	Structure *ecfr.Structure `xml:"-" json:"structure"`
	Citation  SectionCitation `xml:"N,attr" json:"label"`
	Type      string          `xml:"TYPE,attr" json:"node_type"`
	Header    string          `xml:"HEAD" json:"title"`
	Authority string          `xml:"AUTH>PSPACE" json:"-"`
	Source    string          `xml:"SOURCE>PSPACE" json:"-"`
	Children  PartChildren    `xml:",any" json:"children"`
}

func (p *Part) PostProcess() (err error) {
	for _, child := range p.Children {
		c, ok := child.(PostProcesser)
		if ok {
			if err := c.PostProcess(); err != nil {
				return err
			}
		}
	}
	return nil
}

type PartChildren []interface{}

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
		log.Printf("[WARNING] Unknown XML type in Part: %+v\n", start)
		d.Skip()
	}

	return nil
}

type Subpart struct {
	Header   string          `xml:"HEAD" json:"title"`
	Citation SectionCitation `xml:"N,attr" json:"label"`
	Type     string          `xml:"TYPE,attr" json:"node_type"`
	Children SubpartChildren `xml:",any" json:"children"`
}

func (sp *Subpart) PostProcess() error {
	for _, child := range sp.Children {
		c, ok := child.(PostProcesser)
		if ok {
			if err := c.PostProcess(); err != nil {
				return err
			}
		}
	}
	return nil
}

type SubpartChildren []interface{}

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
		log.Printf("[WARNING] Unknown XML type in Subpart: %+v\n", start)
		d.Skip()
	}
	return nil
}

type SubjectGroup struct {
	Header   string               `xml:"HEAD" json:"title"`
	Citation SectionCitation      `xml:"N,attr" json:"label"`
	Type     string               `xml:"TYPE,attr" json:"node_type"`
	Children SubjectGroupChildren `xml:",any" json:"children"`
}

func (sg *SubjectGroup) PostProcess() error {
	for _, child := range sg.Children {
		c, ok := child.(PostProcesser)
		if ok {
			if err := c.PostProcess(); err != nil {
				return err
			}
		}
	}
	return nil
}

type SubjectGroupChildren []interface{}

func (c *SubjectGroupChildren) UnmarshalXML(d *xml.Decoder, start xml.StartElement) error {
	switch start.Name.Local {
	case "DIV8":
		child := &Section{}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	default:
		log.Printf("[WARNING] Unknown XML type in Subject Group: %+v\n", start)
		d.Skip()
	}
	return nil
}

type Section struct {
	Type     string          `xml:"TYPE,attr" json:"node_type"`
	Citation SectionCitation `xml:"N,attr" json:"label"`
	Header   string          `xml:"HEAD" json:"title"`
	Children SectionChildren `xml:",any" json:"children"`
}

func (s *Section) PostProcess() error {
	var prev *Paragraph
	for _, child := range s.Children {
		c, ok := child.(*Paragraph)
		if ok {
			var err error
			c.Citation, err = generateParagraphCitation(c, prev)
			if err != nil && err != ErrNoParents {
				log.Println("[ERROR] generating paragraph citation", err, prev, c)
			} else {
				prev = c
			}

		}
	}
	for _, child := range s.Children {
		c, ok := child.(*Paragraph)
		if ok {
			if len(c.Citation) > 0 {
				cit := append([]string{}, s.Citation...)
				c.Citation = append(cit, c.Citation...)
			} else {
				cit := append([]string{}, s.Citation...)
				c.Citation = append(cit, c.Citation...)
				c.Citation = append(c.Citation, fmt.Sprintf("%x", md5.Sum([]byte(c.Content))))
			}
		}
	}

	for _, child := range s.Children {
		c, ok := child.(PostProcesser)
		if ok {
			if err := c.PostProcess(); err != nil {
				return err
			}
		}
	}
	return nil
}

type SectionChildren []interface{}

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
		log.Printf("[WARNING] Unknown XML type in Section: %+v\n", start)
		d.Skip()
	}

	return nil
}

type SectionCitation []string

func (sl *SectionCitation) UnmarshalText(data []byte) error {
	sections := strings.Split(string(data), "-")
	for _, section := range sections {
		*sl = append(*sl, strings.Split(section, ".")...)
	}
	return nil
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

var ErrNoParents = errors.New("no parents found for this paragraph")
var ErrWrongParent = errors.New("the parent found was of the wrong type")

type Paragraph struct {
	Type     string   `json:"node_type"`
	Content  string   `xml:",innerxml" json:"text"`
	Citation []string `json:"label"`
}

func (p *Paragraph) Marker() ([]string, error) {
	return extractMarker(p.Content)
}

func (p *Paragraph) Level() int {
	if p.Citation != nil {
		return len(p.Citation) - 1
	}
	m, err := p.Marker()
	if err != nil {
		log.Println("[ERROR]", err.Error())
		return -1
	}
	if m == nil {
		return -1
	}
	return matchLabelType(m[len(m)-1])
}
