package parsexml

import (
	"crypto/md5"
	"encoding/xml"
	"errors"
	"fmt"
	"io"
	"strings"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"

	log "github.com/sirupsen/logrus"
)

// LogParseErrors indicates if there were any parsing errors
var LogParseErrors bool

func logParseError(err string) {
	if LogParseErrors {
		log.Warn("[parser] ", err)
	}
}

// PostProcessor interface
type PostProcessor interface {
	PostProcess() error
}

// ParsePart decodes an io.Reader into a regulation Part
func ParsePart(b io.Reader) (*Part, error) {
	d := xml.NewDecoder(b)

	p := &Part{}
	if err := d.Decode(p); err != nil {
		return p, err
	}
	return p, nil
}

// Part is a a regulation Part.
type Part struct {
	XMLName   xml.Name        `xml:"DIV5" json:"-"`
	Structure *ecfr.Structure `xml:"-" json:"structure"`
	Citation  SectionCitation `xml:"N,attr" json:"label"`
	Type      string          `xml:"TYPE,attr" json:"node_type"`
	Header    string          `xml:"HEAD" json:"title"`
	Authority Authority       `xml:"AUTH" json:"authority"`
	Source    Source          `xml:"SOURCE" json:"source"`
	EdNote    EdNote          `xml:"EDNOTE" json:"editorial_note"`
	Children  PartChildren    `xml:",any" json:"children"`
}

// PostProcess is the steps for post processing a Part
func (p *Part) PostProcess() (err error) {
	for _, child := range p.Children {
		c, ok := child.(PostProcessor)
		if ok {
			if err := c.PostProcess(); err != nil {
				return err
			}
		}
	}
	return nil
}

// PartChildren is an array of interface
type PartChildren []interface{}

// UnmarshalXML converts XML to a PartChildren struct
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
		logParseError(fmt.Sprintf("Unknown XML type in part %+v", start))
		d.Skip()
	}

	return nil
}

// Subpart is a Subpart of the regulation
type Subpart struct {
	Header   string          `xml:"HEAD" json:"title"`
	Citation SectionCitation `xml:"N,attr" json:"label"`
	Type     string          `xml:"TYPE,attr" json:"node_type"`
	Children SubpartChildren `xml:",any" json:"children"`
}

// PostProcess defines how to postProcess a subPart
func (sp *Subpart) PostProcess() error {
	for _, child := range sp.Children {
		c, ok := child.(PostProcessor)
		if ok {
			if err := c.PostProcess(); err != nil {
				return err
			}
		}
	}
	return nil
}

// SubpartChildren is an array of interface
type SubpartChildren []interface{}

// UnmarshalXML defines how to unmarshal SubpartChildren from XML
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
	case "DIV9":
		child := &Appendix{}
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
		logParseError(fmt.Sprintf("Unknown XML type in Subpart: %+v", start))
		d.Skip()
	}
	return nil
}

// SubjectGroup is part of the regulation
type SubjectGroup struct {
	Header   XMLString            `xml:"HEAD" json:"title"`
	Citation SectionCitation      `xml:"N,attr" json:"label"`
	Type     string               `xml:"TYPE,attr" json:"node_type"`
	Children SubjectGroupChildren `xml:",any" json:"children"`
}

// XMLString is a struct that holds XML content
type XMLString struct {
	Content string `xml:",innerxml"`
}

// MarshalText converts an XMLString to xml bytes
func (xs XMLString) MarshalText() ([]byte, error) {
	return []byte(xs.Content), nil
}

// PostProcess is the processing of an XMLString after it is unmarshalled
func (sg *SubjectGroup) PostProcess() error {
	for _, child := range sg.Children {
		c, ok := child.(PostProcessor)
		if ok {
			if err := c.PostProcess(); err != nil {
				return err
			}
		}
	}
	return nil
}

// SubjectGroupChildren is an array of interface
type SubjectGroupChildren []interface{}

// UnmarshalXML defines how to unmarshall a SUbjectGroupChildren from XMl
func (c *SubjectGroupChildren) UnmarshalXML(d *xml.Decoder, start xml.StartElement) error {
	switch start.Name.Local {
	case "DIV8":
		child := &Section{}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	case "FTNT":
		child := &FootNote{Type: "FootNote"}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	default:
		logParseError(fmt.Sprintf("Unknown XML type in Subject Group: %+v", start))
		d.Skip()
	}
	return nil
}

// Section is a regulation section
type Section struct {
	Type     string          `xml:"TYPE,attr" json:"node_type"`
	Citation SectionCitation `xml:"N,attr" json:"label"`
	Header   string          `xml:"HEAD" json:"title"`
	Children SectionChildren `xml:",any" json:"children"`
}

// PostProcess cleans up the section after it is imported
func (s *Section) PostProcess() error {
	var prev *Paragraph
	for _, child := range s.Children {
		c, ok := child.(*Paragraph)
		if ok {
			var err error
			c.Citation, err = generateParagraphCitation(c, prev)
			if err != nil && err != ErrNoParents {
				logParseError(fmt.Sprintf("Error generating paragraph citation", err, prev, c))
			} else {
				prev = c
			}
			c.Marker, err = c.marker()
			if err != nil {
				logParseError(fmt.Sprintf("Error generating paragraph marker", err, prev, c))
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
		c, ok := child.(PostProcessor)
		if ok {
			if err := c.PostProcess(); err != nil {
				return err
			}
		}
	}
	return nil
}

// SectionChildren is an array of interface
type SectionChildren []interface{}

// UnmarshalXML defines how to unmarshall XML into SectionChildren
func (c *SectionChildren) UnmarshalXML(d *xml.Decoder, start xml.StartElement) error {
	switch start.Name.Local {
	case "P":
		child := &Paragraph{Type: "Paragraph"}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	case "FP":
		fallthrough
	case "FP-1":
		fallthrough
	case "FP-2":
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
	case "FTNT":
		child := &FootNote{Type: "FootNote"}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	case "DIV":
		child := &Division{Type: "Division"}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	case "EFFDNOT":
		child := &EffectiveDateNote{Type: "EffectiveDateNote"}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	default:
		logParseError(fmt.Sprintf("Unknown XML type in Section: %+v", start))
		d.Skip()
	}

	return nil
}

// SectionCitation is an array of string
type SectionCitation []string

// UnmarshalText converts XML bytes into a SectionCitation struct
func (sl *SectionCitation) UnmarshalText(data []byte) error {
	sections := strings.Split(string(data), "-")
	for _, section := range sections {
		*sl = append(*sl, strings.Split(section, ".")...)
	}
	return nil
}

// Appendix is the struct fro an appendix to the regulation
type Appendix struct {
	Type     string           `xml:"TYPE,attr" json:"node_type"`
	Citation AppendixCitation `xml:"N,attr" json:"label"`
	Header   string           `xml:"HEAD" json:"title"`
	Children AppendixChildren `xml:",any" json:"children"`
}

// AppendixChildren is an unimplemented interface
type AppendixChildren []interface{}

// UnmarshalXML converts XML to AppendixChildren
func (c *AppendixChildren) UnmarshalXML(d *xml.Decoder, start xml.StartElement) error {
	switch start.Name.Local {
	case "P":
		child := &Paragraph{Type: "Paragraph"}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	case "HD1":
		child := &Heading{Type: "Heading"}
		if err := d.DecodeElement(child, &start); err != nil {
			return err
		}
		*c = append(*c, child)
	default:
		logParseError(fmt.Sprintf("Unknown XML type in Appendix: %+v", start))
		d.Skip()
	}

	return nil
}

// AppendixCitation is just an array of string
type AppendixCitation []string

// UnmarshalText creates an AppendixCitation from XML bytes
func (sl *AppendixCitation) UnmarshalText(data []byte) error {
	*sl = strings.Split(string(data), " ")
	return nil
}

// Extract is the essence of something
type Extract struct {
	Type    string `json:"node_type"`
	Content string `xml:",innerxml" json:"content"`
}

// Citation is the citaton for the regulation
type Citation struct {
	Type    string `json:"node_type"`
	Content string `xml:",innerxml" json:"content"`
}

// Source is where the regulation came from
type Source struct {
	Type    string `json:"node_type"`
	Header  string `xml:"HED" json:"header"`
	Content string `xml:"PSPACE" json:"content"`
}

// Authority is the authority behind the regulation
type Authority struct {
	Type    string `json:"node_type"`
	Header  string `xml:"HED" json:"header"`
	Content string `xml:"PSPACE" json:"content"`
}

// EdNote is an editors note
type EdNote struct {
	Type    string `json:"node_type"`
	Header  string `xml:"HED" json:"header"`
	Content string `xml:"PSPACE" json:"content"`
}

// SectionAuthority is the authority behind the section
type SectionAuthority struct {
	Type    string `json:"node_type"`
	Content string `xml:",innerxml" json:"content"`
}

// FlushParagraph is an empty paragraph
type FlushParagraph struct {
	Type    string `json:"node_type"`
	Content string `xml:",innerxml" json:"content"`
}

// Image is a picture in the regulation
type Image struct {
	Type   string `json:"node_type"`
	Source string `xml:"src,attr" json:"src"`
}

// FootNote is a footnote to the regulation
type FootNote struct {
	Type    string `json:"node_type"`
	Content string `xml:",innerxml" json:"content"`
}

// Division is a div in the html
type Division struct {
	Type    string `json:"node_type"`
	Content string `xml:",innerxml" json:"content"`
}

// Heading is a header int he HTML
type Heading struct {
	Type    string `json:"node_type"`
	Content string `xml:",innerxml" json:"content"`
}

// EffectiveDateNote is a note about the effective date of the regulation
type EffectiveDateNote struct {
	Type    string `json:"node_type"`
	Header  string `xml:"HED" json:"header"`
	Content string `xml:"PSPACE" json:"content"`
}

// ErrNoParents is thrown when a paragraph has no parents
var ErrNoParents = errors.New("no parents found for this paragraph")

// ErrWrongParent is thrown when the parent is of the wrong type
var ErrWrongParent = errors.New("the parent found was of the wrong type")

// Paragraph represents a paragraph in the regulation
type Paragraph struct {
	Type     string   `json:"node_type"`
	Content  string   `xml:",innerxml" json:"text"`
	Citation []string `json:"label"`
	Marker   []string `json:"marker"`
}

func (p *Paragraph) marker() ([]string, error) {
	return extractMarker(p.Content)
}

// Level returns how deep a paragraph is in the regulation
func (p *Paragraph) Level() int {
	if p.Citation != nil {
		return len(p.Citation) - 1
	}
	m, err := p.marker()
	if err != nil {
		logParseError(err.Error())
		return -1
	}
	if m == nil {
		return -1
	}
	return matchLabelType(m[len(m)-1])
}
