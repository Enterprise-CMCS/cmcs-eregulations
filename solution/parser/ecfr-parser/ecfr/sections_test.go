package ecfr

import (
	"testing"
	"reflect"
)

func TestExtractStructure(t *testing.T) {
	input := Structure{
		Identifier: IdentifierString{"42"},
		Label: "root",
		LabelLevel: "root",
		LabelDescription: "root",
		Reserved: false,
		Type: "root",
		Children: []*Structure{
			&Structure{
				Identifier: IdentifierString{"root-2"},
				Label: "root-2",
				LabelLevel: "root-2",
				LabelDescription: "root-2",
				Reserved: false,
				Type: "root-2",
				Children: []*Structure{
					&Structure{
						Identifier: IdentifierString{"root-3"},
						Label: "root-3",
						LabelLevel: "root-3",
						LabelDescription: "root-3",
						Reserved: false,
						Type: "root-3",
						Children: []*Structure{
							&Structure{
								Identifier: IdentifierString{"432"},
								Label: "root-4",
								LabelLevel: "root-4",
								LabelDescription: "root-4",
								Reserved: false,
								Type: "root-4",
								Children: []*Structure{
									&Structure{
										Identifier: IdentifierString{"432", "1"},
										Label: "§ 432.1 Basis and purpose.",
										LabelLevel: "§ 432.1",
										LabelDescription: "Basis and purpose.",
										Reserved: false,
										Type: "section",
										Children: []*Structure{},
										DescendantRange: RangeString{},
									},
									&Structure{
										Identifier: IdentifierString{"A"},
										Label: "Subpart A - General Provisions",
										LabelLevel: "Subpart A",
										LabelDescription: "General Provisions",
										Reserved: false,
										Type: "subpart",
										Children: []*Structure{
											&Structure{
												Identifier: IdentifierString{"432", "3"},
												Label: "§ 432.3 test432.3",
												LabelLevel: "§ 432.3",
												LabelDescription: "test432.3",
												Reserved: false,
												Type: "section",
												Children: []*Structure{},
												DescendantRange: RangeString{},
											},
											&Structure{
												Identifier: IdentifierString{"432", "4"},
												Label: "§ 432.4 test432.4",
												LabelLevel: "§ 432.4",
												LabelDescription: "test432.4",
												Reserved: false,
												Type: "section",
												Children: []*Structure{},
												DescendantRange: RangeString{},
											},
										},
										DescendantRange: RangeString{"432.3", "432.4"},
									},
									&Structure{
										Identifier: IdentifierString{"ECFR14123c518724401"},
										Label: "General Provisions",
										LabelLevel: "General Provisions",
										LabelDescription: "General Provisions",
										Reserved: false,
										Type: "subject_group",
										Children: []*Structure{
											&Structure{
												Identifier: IdentifierString{"432", "200"},
												Label: "§ 432.200 Basis and scope.",
												LabelLevel: "§ 432.200",
												LabelDescription: "Basis and scope.",
												Reserved: false,
												Type: "section",
												Children: []*Structure{},
												DescendantRange: RangeString{},
											},
											&Structure{
												Identifier: IdentifierString{"432", "201"},
												Label: "§ 432.201 ASDFGH.",
												LabelLevel: "§ 432.201",
												LabelDescription: "ASDFGH.",
												Reserved: false,
												Type: "section",
												Children: []*Structure{},
												DescendantRange: RangeString{},
											},
										},
										DescendantRange: RangeString{"431.200", "431.201"},
									},
								},
								DescendantRange: RangeString{"432.1", "432.201"},
							},
						},
						DescendantRange: RangeString{},
					},
				},
				DescendantRange: RangeString{},
			},
		},
		DescendantRange: RangeString{},
	}

	expected := Part{
		Name: "432",
		Title: "42",
		Sections: []Section{
			Section{
				Title: "42",
				Part: "432",
				Section: "1",
			},
		},
		Subparts: []Subpart{
			Subpart{
				Title: "42",
				Part: "432",
				Subpart: "A",
				Sections: []Section{
					Section{
						Title: "42",
						Part: "432",
						Section: "3",
					},
					Section{
						Title: "42",
						Part: "432",
						Section: "4",
					},
				},
			},
		},
	}

	output, _ := ExtractStructure(input)
	if !reflect.DeepEqual(output, expected) {
		t.Errorf("expected (%+v), received (%+v)", expected, output)
	}
}

func TestExtractSubpart(t *testing.T) {
	testTable := []struct {
		Name string
		Input Structure
		Expected Subpart
	}{
		{
			Name: "test-single-section-child",
			Input: Structure{
				Identifier: IdentifierString{"A"},
				Label: "Subpart A - General Provisions",
				LabelLevel: "Subpart A",
				LabelDescription: "General Provisions",
				Reserved: false,
				Type: "subpart",
				Children: []*Structure{
					&Structure{
						Identifier: IdentifierString{"432", "1"},
						Label: "§ 432.1 Basis and purpose.",
						LabelLevel: "§ 432.1",
						LabelDescription: "Basis and purpose.",
						Reserved: false,
						Type: "section",
						Children: []*Structure{},
						DescendantRange: RangeString{},
					},
				},
				DescendantRange: RangeString{"432.1", "432.10"},
			},
			Expected: Subpart{
				Title: "42",
				Part: "432",
				Subpart: "A",
				Sections: []Section{
					Section{
						Title: "42",
						Part: "432",
						Section: "1",
					},
				},
			},
		},
		{
			Name: "test-multiple-section-children",
			Input: Structure{
				Identifier: IdentifierString{"A"},
				Label: "Subpart A - General Provisions",
				LabelLevel: "Subpart A",
				LabelDescription: "General Provisions",
				Reserved: false,
				Type: "subpart",
				Children: []*Structure{
					&Structure{
						Identifier: IdentifierString{"432", "1"},
						Label: "§ 432.1 Basis and purpose.",
						LabelLevel: "§ 432.1",
						LabelDescription: "Basis and purpose.",
						Reserved: false,
						Type: "section",
						Children: []*Structure{},
						DescendantRange: RangeString{},
					},
					&Structure{
						Identifier: IdentifierString{"432", "2"},
						Label: "§ 432.2 ASDF.",
						LabelLevel: "§ 432.2",
						LabelDescription: "ASDF.",
						Reserved: false,
						Type: "section",
						Children: []*Structure{},
						DescendantRange: RangeString{},
					},
					&Structure{
						Identifier: IdentifierString{"432", "3"},
						Label: "§ 432.3 QWERTY.",
						LabelLevel: "§ 432.3",
						LabelDescription: "QWERTY.",
						Reserved: false,
						Type: "section",
						Children: []*Structure{},
						DescendantRange: RangeString{},
					},
				},
				DescendantRange: RangeString{"432.1", "432.10"},
			},
			Expected: Subpart{
				Title: "42",
				Part: "432",
				Subpart: "A",
				Sections: []Section{
					Section{
						Title: "42",
						Part: "432",
						Section: "1",
					},
					Section{
						Title: "42",
						Part: "432",
						Section: "2",
					},
					Section{
						Title: "42",
						Part: "432",
						Section: "3",
					},
				},
			},
		},
		{
			Name: "test-subject-group-children",
			Input: Structure{
				Identifier: IdentifierString{"A"},
				Label: "Subpart A - General Provisions",
				LabelLevel: "Subpart A",
				LabelDescription: "General Provisions",
				Reserved: false,
				Type: "subpart",
				Children: []*Structure{
					&Structure{
						Identifier: IdentifierString{"432", "1"},
						Label: "§ 432.1 Basis and purpose.",
						LabelLevel: "§ 432.1",
						LabelDescription: "Basis and purpose.",
						Reserved: false,
						Type: "section",
						Children: []*Structure{},
						DescendantRange: RangeString{},
					},
					&Structure{
						Identifier: IdentifierString{"ECFR14123c518724401"},
						Label: "General Provisions",
						LabelLevel: "General Provisions",
						LabelDescription: "General Provisions",
						Reserved: false,
						Type: "subject_group",
						Children: []*Structure{
							&Structure{
								Identifier: IdentifierString{"432", "200"},
								Label: "§ 432.200 Basis and scope.",
								LabelLevel: "§ 432.200",
								LabelDescription: "Basis and scope.",
								Reserved: false,
								Type: "section",
								Children: []*Structure{},
								DescendantRange: RangeString{},
							},
							&Structure{
								Identifier: IdentifierString{"432", "201"},
								Label: "§ 432.201 ASDFGH.",
								LabelLevel: "§ 432.201",
								LabelDescription: "ASDFGH.",
								Reserved: false,
								Type: "section",
								Children: []*Structure{},
								DescendantRange: RangeString{},
							},
						},
						DescendantRange: RangeString{"431.200", "431.206"},
					},
				},
				DescendantRange: RangeString{"432.1", "432.10"},
			},
			Expected: Subpart{
				Title: "42",
				Part: "432",
				Subpart: "A",
				Sections: []Section{
					Section{
						Title: "42",
						Part: "432",
						Section: "1",
					},
					Section{
						Title: "42",
						Part: "432",
						Section: "200",
					},
					Section{
						Title: "42",
						Part: "432",
						Section: "201",
					},
				},
			},
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			output := extractSubpart("42", "432", &tc.Input)
			if !reflect.DeepEqual(output, tc.Expected) {
				t.Errorf("expected (%+v), received (%+v)", tc.Expected, output)
			}
		})
	}
}

func TestExtractSection(t *testing.T) {
	input := Structure{
		Identifier: IdentifierString{"432", "1"},
		Label: "§ 432.1 Basis and purpose.",
		LabelLevel: "§ 432.1",
		LabelDescription: "Basis and purpose.",
		Reserved: false,
		Type: "section",
		Children: []*Structure{},
		DescendantRange: RangeString{},
	}

	expected := Section{
		Title: "42",
		Part: "432",
		Section: "1",
	}

	output := extractSection("42", &input)
	if !reflect.DeepEqual(output, expected) {
		t.Errorf("expected (%+v), received (%+v)", expected, output)
	}
}
