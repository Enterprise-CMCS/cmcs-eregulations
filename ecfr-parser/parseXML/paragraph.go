package parseXML

import (
	"fmt"
	"log"
	"regexp"
)

func generateParagraphCitation(p *Paragraph, s *Section) ([]string, error) {
	citation := []string{}
	pLabel, err := p.Marker()
	if err != nil {
		return citation, err
	}
	if len(pLabel) == 0 {
		return citation, nil
	}
	currentLevel := matchLabelType(pLabel[0])
	if currentLevel == 0 {
		citation = append(citation, s.Citation...)
		citation = append(citation, pLabel...)
		log.Println("[DEBUG] top level paragraph", citation)
		return citation, nil
	}

	if currentLevel == 2 {
		// then it might really be a level 0
		sibs, err := extractOlderSiblings(p, s.Children)
		if err != nil {
			return citation, err
		}

		ps := firstParentOrSib(p, sibs)
		if ps == nil {
			return citation, ErrNoParents
		}
		parentOrFirstSib, ok := ps.(*Paragraph)
		if !ok {
			return citation, ErrWrongParent
		}
		if parentOrFirstSib.Level() == 0 {
			p.Citation = append(p.Citation, s.Citation...)
			p.Citation = append(p.Citation, pLabel...)
			log.Println("[DEBUG] top level paragraph", p.Citation)
			return citation, nil
		}
	}

	sibs, err := extractOlderSiblings(p, s.Children)
	if err != nil {
		return citation, err
	}

	ps := firstParentOrSib(p, sibs)
	if ps == nil {
		return citation, ErrNoParents
	}
	parentOrFirstSib, ok := ps.(*Paragraph)
	if !ok {
		log.Printf("[ERROR] %+v \n", parentOrFirstSib)
		return citation, ErrWrongParent
	}

	if len(parentOrFirstSib.Citation) == 0 {
		return citation, nil
	}

	// if it's the direct parent, use the whole thing
	if parentOrFirstSib.Level() < currentLevel {
		citation = append(citation, parentOrFirstSib.Citation...)
	} else if parentOrFirstSib.Level() == currentLevel {
		// if it's the sib use all but the last element
		citation = append(citation, parentOrFirstSib.Citation[:len(parentOrFirstSib.Citation)-1]...)
	}

	return append(citation, pLabel...), nil
}

type Leveled interface {
	Level() int
}

// a, 1, roman, upper, italic int, italic roman
var alpha = regexp.MustCompile(`([a-z])`)
var num = regexp.MustCompile(`(\d+)`)
var roman = regexp.MustCompile(`(x|ix|iv|v|vi{1,3}|i{1,3})`)
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

// assumes sibs are ordered starting with the closest to the element
func firstParentOrSib(el Leveled, sibs []interface{}) interface{} {
	pLevel := el.Level()
	for _, unknownSib := range sibs {
		sib, ok := unknownSib.(Leveled)
		if !ok {
			continue
		}
		l := sib.Level()

		// handles cases of malformed identifiers (e.g. (1) with no parent (a))
		if l < 0 {
			continue
		}

		if l <= pLevel {
			return sib
		}
	}
	return nil
}

func extractMarker(l string) ([]string, error) {
	// TODO: This can be pulled out into a module level var
	re := regexp.MustCompile(`^\(([^\)]+)\)(?:(?: ?<I>.+<\/I> ?)?\(([^\)]+)\))?`)
	pLabel := re.FindStringSubmatch(l)
	if len(pLabel) == 0 {
		return nil, nil
	}
	if len(pLabel) < 2 {
		return nil, fmt.Errorf("wrong number of labels")
	}
	// TODO: can this case really be reached still?
	if len(pLabel) == 3 && pLabel[2] == "" {
		pLabel = pLabel[:2]
	}
	pLabel = pLabel[1:]
	return pLabel, nil
}
