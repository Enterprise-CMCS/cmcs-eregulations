package parseXML

import (
	"fmt"
	"regexp"
)

var re = regexp.MustCompile(`^\(([^\)]+)\)(?:(?: ?<I>[^<]+<\/I>(?: ?-)?)? ?\(([^\)]{1,3})\))?(?: ?(?:<I>[^<]+<\/I>(?: ?-)?)? ?\(([^\)]{1,3})\))?`)

func generateParagraphCitation(p *Paragraph, prev *Paragraph) ([]string, error) {
	citation := []string{}
	pLabel, err := p.marker()
	if err != nil {
		return citation, err
	}

	if len(pLabel) == 0 {
		return citation, nil
	}

	currentLevel := matchLabelType(pLabel[0])
	if currentLevel == 0 {
		citation = append(citation, pLabel...)
		return citation, nil
	}

	if prev == nil || len(prev.Citation) == 0 {
		if currentLevel != 0 {
			return nil, nil
		}
		return pLabel, nil
	}

	if currentLevel == 2 {
		if len(pLabel) > 1 {
			if matchLabelType(pLabel[1]) == 1 {
				citation = append(p.Citation, pLabel...)
				return citation, nil
			}
		}
		if pLabel[0] == "i" {
			if prev.Level() != 1 {
				citation = append(p.Citation, pLabel...)
				return citation, nil
			}
		}
		if pLabel[0] == "v" {
			if len(prev.Citation) < 3 {
				citation = append(p.Citation, pLabel...)
				return citation, nil
			} else if prev.Citation[2] != "iv" {
				citation = append(p.Citation, pLabel...)
				return citation, nil
			}
		}
	}

	if prev.Level()-currentLevel < -1 {
		return nil, fmt.Errorf("this paragrpah and it's neighbor are not in the right order %+v %+v", prev, p)
	}

	l := currentLevel
	if len(prev.Citation) < currentLevel {
		if currentLevel-1 != len(prev.Citation) {
			return nil, fmt.Errorf("this paragrpah and it's neighbor are not in the right order %+v %+v", prev, p)
		}
		l--
	}

	citation = append(citation, prev.Citation[:l]...)

	return append(citation, pLabel...), nil
}

// a, 1, roman, upper, italic int, italic roman
var alpha = regexp.MustCompile(`([a-z])`)
var num = regexp.MustCompile(`(\d+)`)
var roman = regexp.MustCompile(`(x|ix|iv|v|vi{1,3}|i{1,3})`)
var upper = regexp.MustCompile(`([A-Z])`)
var italic_num = regexp.MustCompile(`(<I>\d+<\/I>)`)
var italic_roman = regexp.MustCompile(`<I>(ix|iv|v|vi{1,3}|i{1,3})<\/I>`)

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

func extractMarker(l string) ([]string, error) {
	pLabel := re.FindStringSubmatch(l)
	if len(pLabel) == 0 {
		return nil, nil
	}
	if len(pLabel) < 2 {
		return nil, fmt.Errorf("wrong number of labels")
	}
	if len(pLabel) == 3 && pLabel[2] == "" {
		pLabel = pLabel[:2]
	}

	if len(pLabel) == 4 {
		if pLabel[2] == "" {
			pLabel = pLabel[:2]
		} else if pLabel[3] == "" {
			pLabel = pLabel[:3]
		}
	}
	pLabel = pLabel[1:]
	return pLabel, nil
}
