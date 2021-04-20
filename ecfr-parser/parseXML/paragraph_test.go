package parseXML

import "testing"

/*
level = level of last element
parent or direct sibling = level <= current

"(a)"
"(1)"

a

"a,1"

"(a)(1)"
"(2)"

a

"a,2"

"(a)(1)"
"(i)" "-> a.1.i"

1

"a,1,i"

"(1)"

"vs roman numeral"
"i"
*/

type exampleLevel string

func (e exampleLevel) Level() int {
	m, _ := extractMarker(string(e))
	return matchLabelType(m[len(m)-1])
}

func TestFirstParent(t *testing.T) {
	tests := []struct {
		input struct {
			el   Leveled
			sibs []interface{}
		}
		output exampleLevel
	}{
		{
			input: struct {
				el   Leveled
				sibs []interface{}
			}{
				exampleLevel("(1)"),
				[]interface{}{
					exampleLevel("(a)"),
				},
			},
			output: exampleLevel("(a)"),
		},
		{
			input: struct {
				el   Leveled
				sibs []interface{}
			}{
				exampleLevel("(2)"),
				[]interface{}{
					exampleLevel("(2)"),
				},
			},
			output: exampleLevel("(2)"),
		},
		{
			input: struct {
				el   Leveled
				sibs []interface{}
			}{
				exampleLevel("(2)"),
				[]interface{}{
					exampleLevel("(i)"),
					exampleLevel("(a)(1)"),
				},
			},
			output: exampleLevel("(a)(1)"),
		},
		{
			input: struct {
				el   Leveled
				sibs []interface{}
			}{
				exampleLevel("(2)"),
				[]interface{}{
					exampleLevel("(i)"),
					exampleLevel("(a)(1)"),
				},
			},
			output: exampleLevel("(a)(1)"),
		},
		{
			input: struct {
				el   Leveled
				sibs []interface{}
			}{
				exampleLevel("(i)"),
				[]interface{}{
					exampleLevel("(a)(2)"),
				},
			},
			output: exampleLevel("(a)(2)"),
		},
		{
			input: struct {
				el   Leveled
				sibs []interface{}
			}{
				exampleLevel("(i)(A)"),
				[]interface{}{
					exampleLevel("(3)"),
				},
			},
			output: exampleLevel("(3)"),
		},
	}

	for _, test := range tests {
		result := firstParentOrSib(test.input.el, test.input.sibs)
		if result != test.output {
			t.Errorf("%+v didn't equal expected %+v", result, test.output)
		}
	}
}
