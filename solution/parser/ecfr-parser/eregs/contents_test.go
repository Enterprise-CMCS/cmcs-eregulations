package eregs

import (
	"testing"

	"github.com/go-test/deep"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"
)

func TestAddPart(t *testing.T) {
	title := Title{
		Name: "42",
		Contents: &ecfr.Structure{},
	}

	firstAddition := Title{
		Name: "42",
		Contents: &ecfr.Structure{
			Identifier: ecfr.IdentifierString{"42"},
			Type: "title",
			Children: []*ecfr.Structure{
				&ecfr.Structure{
					Identifier: ecfr.IdentifierString{"A"},
					Type: "subchapter",
					Children: []*ecfr.Structure{
						&ecfr.Structure{
							Identifier: ecfr.IdentifierString{"400"},
							Type: "part",
							Children: []*ecfr.Structure{},
						},
					},
				},
			},
		},
	}

	title.AddPart(firstAddition.Contents, "400")

	if diff := deep.Equal(title, firstAddition); diff != nil {
		t.Errorf("first pass output not as expected: %+v", diff)
	}

	secondAddition := ecfr.Structure{
		Identifier: ecfr.IdentifierString{"42"},
		Type: "title",
		Children: []*ecfr.Structure{
			&ecfr.Structure{
				Identifier: ecfr.IdentifierString{"A"},
				Type: "subchapter",
				Children: []*ecfr.Structure{
					&ecfr.Structure{
						Identifier: ecfr.IdentifierString{"401"},
						Type: "part",
						Children: []*ecfr.Structure{},
					},
				},
			},
		},	
	}

	secondExpected := Title{
		Name: "42",
		Contents: &ecfr.Structure{
			Identifier: ecfr.IdentifierString{"42"},
			Type: "title",
			Children: []*ecfr.Structure{
				&ecfr.Structure{
					Identifier: ecfr.IdentifierString{"A"},
					Type: "subchapter",
					Children: []*ecfr.Structure{
						&ecfr.Structure{
							Identifier: ecfr.IdentifierString{"400"},
							Type: "part",
							Children: []*ecfr.Structure{},
						},
						&ecfr.Structure{
							Identifier: ecfr.IdentifierString{"401"},
							Type: "part",
							Children: []*ecfr.Structure{},
						},
					},
				},
			},
		},
	}

	title.AddPart(&secondAddition, "401")

	if diff := deep.Equal(title, secondExpected); diff != nil {
		t.Errorf("second pass output not as expected: %+v", diff)
	}

	title.AddPart(&secondAddition, "401")

	if diff := deep.Equal(title, secondExpected); diff != nil {
		t.Errorf("output not as expected while updating a part: %+v", diff)
	}
}

func TestRemovePart(t *testing.T) {
	start := Title{
		Name: "42",
		Contents: &ecfr.Structure{
			Identifier: ecfr.IdentifierString{"42"},
			Type: "title",
			Children: []*ecfr.Structure{
				&ecfr.Structure{
					Identifier: ecfr.IdentifierString{"A"},
					Type: "subchapter",
					Children: []*ecfr.Structure{
						&ecfr.Structure{
							Identifier: ecfr.IdentifierString{"400"},
							Type: "part",
							Children: []*ecfr.Structure{},
						},
						&ecfr.Structure{
							Identifier: ecfr.IdentifierString{"401"},
							Type: "part",
							Children: []*ecfr.Structure{},
						},
					},
				},
			},
		},
	}

	first := Title{
		Name: "42",
		Contents: &ecfr.Structure{
			Identifier: ecfr.IdentifierString{"42"},
			Type: "title",
			Children: []*ecfr.Structure{
				&ecfr.Structure{
					Identifier: ecfr.IdentifierString{"A"},
					Type: "subchapter",
					Children: []*ecfr.Structure{
						&ecfr.Structure{
							Identifier: ecfr.IdentifierString{"401"},
							Type: "part",
							Children: []*ecfr.Structure{},
						},
					},
				},
			},
		},
	}

	err := start.RemovePart("400")

	if diff := deep.Equal(start, first); diff != nil {
		t.Errorf("first pass output not as expected: %+v", diff)
	}

	if err != nil {
		t.Errorf("received error (%+v)", err)
	}

	second := Title{
		Name: "42",
		Contents: &ecfr.Structure{
			Identifier: ecfr.IdentifierString{"42"},
			Type: "title",
			Children: []*ecfr.Structure{},
		},
	}

	err = start.RemovePart("401")

	if diff := deep.Equal(start, second); diff != nil {
		t.Errorf("second pass output not as expected: %+v", diff)
	}

	if err != nil {
		t.Errorf("received error (%+v)", err)
	}

	err = start.RemovePart("100")

	if err == nil {
		t.Errorf("expected error, received none")
	}
}

func TestIdentifierStringEqual(t *testing.T) {
	testTable := []struct{
		Name string
		One ecfr.IdentifierString
		Two ecfr.IdentifierString
		Equal bool
	}{
		{
			Name: "test-single-element-equal",
			One: ecfr.IdentifierString{"A"},
			Two: ecfr.IdentifierString{"A"},
			Equal: true,
		},
		{
			Name: "test-two-elements-equal",
			One: ecfr.IdentifierString{"A", "42"},
			Two: ecfr.IdentifierString{"A", "42"},
			Equal: true,
		},
		{
			Name: "test-length-not-equal",
			One: ecfr.IdentifierString{"A"},
			Two: ecfr.IdentifierString{"A", "B"},
			Equal: false,
		},
		{
			Name: "test-not-equal",
			One: ecfr.IdentifierString{"A"},
			Two: ecfr.IdentifierString{"B"},
			Equal: false,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			equal := identifierStringEqual(&tc.One, &tc.Two)
			if equal && !tc.Equal {
				t.Errorf("expected not equal, got equal")
			} else if !equal && tc.Equal {
				t.Errorf("expected equal, got not equal")
			}
		})
	}
}

func TestCopyStructure(t *testing.T) {
	a := ecfr.Structure{
		Identifier: ecfr.IdentifierString{"A", "B"},
		Label: "Test",
		LabelLevel: "TestLevel",
		LabelDescription: "TestDescription",
		Reserved: true,
		Type: "title",
		Children: []*ecfr.Structure{
			&ecfr.Structure{
				Identifier: ecfr.IdentifierString{"42"},
			},
		},
		DescendantRange: ecfr.RangeString{"abc", "xyz"},
	}

	expected := ecfr.Structure{
		Identifier: ecfr.IdentifierString{"A", "B"},
		Label: "Test",
		LabelLevel: "TestLevel",
		LabelDescription: "TestDescription",
		Reserved: true,
		Type: "title",
		Children: []*ecfr.Structure{},
		DescendantRange: ecfr.RangeString{"abc", "xyz"},
	}

	output := copyStructure(&a)

	if diff := deep.Equal(&expected, output); diff != nil {
		t.Errorf("output not as expected: %+v", diff)
	}
}
