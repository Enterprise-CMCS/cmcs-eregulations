package parseXML

import (
	"fmt"
	"log"
	"regexp"
)

type Markable interface {
	Marker() ([]string, error)
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

func firstParent(pLevel int, sibs []interface{}) []string {

	for _, unknownSib := range sibs {
		sib, ok := unknownSib.(*Paragraph)
		if !ok {
			continue
		}
		sibLabel, err := sib.Marker()
		if err != nil {
			log.Println("[ERROR]", err)
			continue
		}

		// handles cases of malformed identifiers (e.g. (1) with no parent (a))
		if sibLabel == nil || len(sib.Citation) == 0 {
			continue
		}

		l := sibLabel[len(sibLabel)-1]
		// Note: the option is to look at the length of the citation to get the level
		subLevel := matchLabelType(l)

		if subLevel == pLevel {
			// could also use this as a spot to do some error checking
			// e.g. if it's a sibling and not in order
			return sib.Citation[:len(sib.Citation)-1]
		}

		// TODO: should be specific, if it's not exactly one level up something's wrong
		if subLevel == (pLevel - 1) {
			return sib.Citation
		}

		if subLevel < (pLevel - 1) {
			/* if one of these cases has happened it's acceptable
			h
			i

			u
			v

			w
			x
			*/

			if sibLabel[0] == "h" || sibLabel[0] == "u" || sibLabel[0] == "w" {
				return sib.Citation[:len(sib.Citation)-1]
			}

			log.Fatal("An element had unordered older siblings", subLevel, pLevel, sibLabel)
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
