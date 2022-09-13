package ecfr

import (
	"testing"

	"github.com/go-test/deep"
)

func TestExtractStructure(t *testing.T) {
	input := Structure{
		Identifier:       IdentifierString{"42"},
		Label:            "Title 42 - Public Health",
		LabelLevel:       "Title 42",
		LabelDescription: "Public Health",
		Reserved:         false,
		Type:             "title",
		Children: []*Structure{
			&Structure{
				Identifier:       IdentifierString{"IV"},
				Label:            "Chapter IV - Centers for Medicare & Medicaid Services, Department of Health and Human Services",
				LabelLevel:       "Chapter IV",
				LabelDescription: "Centers for Medicare &amp; Medicaid Services, Department of Health and Human Services",
				Reserved:         false,
				Type:             "chapter",
				Children: []*Structure{
					&Structure{
						Identifier:       IdentifierString{"C"},
						Label:            "Subchapter C - Medical Assistance Programs",
						LabelLevel:       "Subchapter C",
						LabelDescription: "Subchapter C",
						Reserved:         false,
						Type:             "subchapter",
						Children: []*Structure{
							&Structure{
								Identifier:       IdentifierString{"432"},
								Label:            "Part 432",
								LabelLevel:       "Part 432",
								LabelDescription: "Part 432",
								Reserved:         false,
								Type:             "part",
								Children: []*Structure{
									&Structure{
										Identifier:       IdentifierString{"432", "1"},
										Label:            "§ 432.1 Basis and purpose.",
										LabelLevel:       "§ 432.1",
										LabelDescription: "Basis and purpose.",
										Reserved:         false,
										Type:             "section",
										Children:         []*Structure{},
										DescendantRange:  RangeString{},
									},
									&Structure{
										Identifier:       IdentifierString{"432", "2"},
										Label:            "§ 432.2 Reserved",
										LabelLevel:       "§ 432.2",
										LabelDescription: "Reserved",
										Reserved:         true,
										Type:             "section",
										Children:         []*Structure{},
										DescendantRange:  RangeString{},
									},
									&Structure{
										Identifier:       IdentifierString{"A"},
										Label:            "Subpart A - General Provisions",
										LabelLevel:       "Subpart A",
										LabelDescription: "General Provisions",
										Reserved:         false,
										Type:             "subpart",
										Children: []*Structure{
											&Structure{
												Identifier:       IdentifierString{"432", "3"},
												Label:            "§ 432.3 test432.3",
												LabelLevel:       "§ 432.3",
												LabelDescription: "test432.3",
												Reserved:         false,
												Type:             "section",
												Children:         []*Structure{},
												DescendantRange:  RangeString{},
											},
											&Structure{
												Identifier:       IdentifierString{"432", "4"},
												Label:            "§ 432.4 test432.4",
												LabelLevel:       "§ 432.4",
												LabelDescription: "test432.4",
												Reserved:         false,
												Type:             "section",
												Children:         []*Structure{},
												DescendantRange:  RangeString{},
											},
											&Structure{
												Identifier:       IdentifierString{"ECFR14123c518724401"},
												Label:            "General Provisions",
												LabelLevel:       "General Provisions",
												LabelDescription: "General Provisions",
												Reserved:         false,
												Type:             "subject_group",
												Children: []*Structure{
													&Structure{
														Identifier:       IdentifierString{"432", "200"},
														Label:            "§ 432.200 Basis and scope.",
														LabelLevel:       "§ 432.200",
														LabelDescription: "Basis and scope.",
														Reserved:         false,
														Type:             "section",
														Children:         []*Structure{},
														DescendantRange:  RangeString{},
													},
													&Structure{
														Identifier:       IdentifierString{"432", "201"},
														Label:            "§ 432.201 ASDFGH.",
														LabelLevel:       "§ 432.201",
														LabelDescription: "ASDFGH.",
														Reserved:         false,
														Type:             "section",
														Children:         []*Structure{},
														DescendantRange:  RangeString{},
													},
												},
												DescendantRange: RangeString{"431.200", "431.201"},
											},
										},
										DescendantRange: RangeString{"432.3", "432.4"},
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

	depth := 3

	expectedSections := []Section{
		Section{
			Title: "42",
			Part: "432",
			Section: "1",
		},
	}

	expectedSubparts := []Subpart{
		Subpart{
			Title:   "42",
			Part:    "432",
			Subpart: "A",
			Sections: []Section{
				Section{
					Title:   "42",
					Part:    "432",
					Section: "3",
				},
				Section{
					Title:   "42",
					Part:    "432",
					Section: "4",
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
	}

	sections, subparts, err := ExtractStructure(input, depth)
	if diff := deep.Equal(sections, expectedSections); diff != nil {
		t.Errorf("sections not as expected: (%+v)", diff)
	}
	if diff := deep.Equal(subparts, expectedSubparts); diff != nil {
		t.Errorf("subparts not as expected: (%+v)", diff)
	}
	if err != nil {
		t.Errorf("received error: (%+v)", err)
	}
}
