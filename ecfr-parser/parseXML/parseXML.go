package parseXML

import (
	"encoding/xml"
	"errors"
	"fmt"
	"io"
	"log"
	"strings"
)

func ParsePart(b io.ReadCloser) (*Part, error) {
	d := xml.NewDecoder(b)

	p := &Part{}
	log.Println("[DEBUG] Decoding part")
	if err := d.Decode(p); err != nil {
		return p, err
	}
	return p, nil
}

type Part struct {
	XMLName   xml.Name     `xml:"DIV5"`
	Name      string       `xml:"N,attr"`
	Type      string       `xml:"TYPE,attr"`
	Header    string       `xml:"HEAD"`
	Authority string       `xml:"AUTH>PSPACE"`
	Source    string       `xml:"SOURCE>PSPACE"`
	Children  PartChildren `xml:",any"`
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
		//return fmt.Errorf("Unknown XML type in Part: %+v", start)
		fmt.Printf("Unknown XML type in Part: %+v\n", start)
		d.Skip()
	}

	return nil
}

type Subpart struct {
	Header   string          `xml:"HEAD"`
	Name     string          `xml:"N,attr"`
	Type     string          `xml:"TYPE,attr"`
	Children SubpartChildren `xml:",any"`
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
		//return fmt.Errorf("Unknown XML type in Subpart: %+v", start)
		fmt.Printf("Unknown XML type in Subpart: %+v\n", start)
		d.Skip()
	}
	return nil
}

type SubjectGroup struct {
	Header   string               `xml:"HEAD"`
	Name     string               `xml:"N,attr"`
	Type     string               `xml:"TYPE,attr"`
	Children SubjectGroupChildren `xml:",any"`
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
		//return fmt.Errorf("Unknown XML type in Subpart: %+v", start)
		fmt.Printf("Unknown XML type in Subject Group: %+v\n", start)
		d.Skip()
	}
	return nil
}

type Section struct {
	Type     string          `xml:"TYPE,attr"`
	Citation SectionCitation `xml:"N,attr"`
	Header   string          `xml:"HEAD"`
	Children SectionChildren `xml:",any"`
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
		//return fmt.Errorf("Unknown XML type in Section: %+v", start)
		fmt.Printf("Unknown XML type in Section: %+v\n", start)
		d.Skip()
	}

	return nil
}

type SectionCitation []string

func (sl *SectionCitation) UnmarshalText(data []byte) error {
	*sl = strings.Split(string(data), ".")
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
	Type     string
	Content  string `xml:",innerxml"`
	Citation []string
}

func (p *Paragraph) Marker() ([]string, error) {
	return extractMarker(p.Content)
}

func (p *Paragraph) Level() int {
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

// TODO: I'd like to get rid of the explicit dependency on Section
func (p *Paragraph) PostProcess(s *Section) (err error) {
	p.Citation, err = generateParagraphCitation(p, s)
	return
}

type PostProcesser interface {
	PostProcess(s *Section) error
}
