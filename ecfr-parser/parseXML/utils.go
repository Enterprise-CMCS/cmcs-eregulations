package parseXML

import "fmt"

func extractOlderSiblings(p interface{}, allChildren []interface{}) ([]interface{}, error) {
	index := -1
	for i, c := range allChildren {
		if c == p {
			index = i
			break
		}
	}
	if index < 0 {
		return nil, fmt.Errorf("could not find element in section")
	}
	sibs := []interface{}{}
	for _, c := range allChildren[:index] {
		sibs = append([]interface{}{c}, sibs...)
	}
	return sibs, nil
}
