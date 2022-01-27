package parsexml

import (
	"testing"
	"reflect"
	"encoding/xml"
	"bytes"
)

func TestParsePart(t *testing.T) {
	testTable := []struct {
		Name string
		Input []byte
		Expected Part
		Error bool
	}{
		{
			Name: "test-valid-part",
			Input: []byte(`
				<DIV5 N="433" TYPE="PART">
					<HEAD>PART 399 - EMPLOYEE SAFETY AND HEALTH STANDARDS</HEAD>
					<AUTH>
						<HED>Authority:</HED>
						<PSPACE>49 U.S.C. 31502; and 49 CFR 1.87. </PSPACE>
					</AUTH>
					<SOURCE>
						<HED>Source:</HED>
						<PSPACE>44 FR 43732, July 26, 1979, unless otherwise noted. </PSPACE>
					</SOURCE>
					<DIV6 N="L" TYPE="SUBPART">
						<HEAD>Subpart L - Step, Handhold, and Deck Requirements...</HEAD>
						<DIV7 N="ECFRb511534bf191cab" TYPE="SUBJGRP">
							<HEAD>Assignment of Rights to Benefits</HEAD>
							<DIV8 N="433.145" TYPE="SECTION" VOLUME="4">
								<HEAD>§ 433.145 Assignment of rights to benefits - State plan requirements.</HEAD>
								<P>(a) A State plan must provide that, as a condition of eligibility, each legally...</P>
								<P>(1) Assign to the Medicaid agency his or her rights, or the rights of any other...</P>
							</DIV8>
						</DIV7>
					</DIV6>
					<DIV8 N="433.146" TYPE="SECTION" VOLUME="4">
						<HEAD>§ 433.146 Rights assigned; assignment method.</HEAD>
						<P>(a) Except as specified in paragraph (b) of this section, the agency must require...</P>
					</DIV8>
				</DIV5>
			`),
			Expected: Part{
				XMLName: xml.Name{
					Space: "",
					Local: "DIV5",
				},
				Citation: SectionCitation{"433"},
				Type: "PART",
				Header: "PART 399 - EMPLOYEE SAFETY AND HEALTH STANDARDS",
				Authority: Authority{
					Header: "Authority:",
					Content: "49 U.S.C. 31502; and 49 CFR 1.87. ",
				},
				Source: Source{
					Header: "Source:",
					Content: "44 FR 43732, July 26, 1979, unless otherwise noted. ",
				},
				Children: PartChildren{
					&Subpart{
						Type: "SUBPART",
						Citation: SectionCitation{"L"},
						Header: "Subpart L - Step, Handhold, and Deck Requirements...",
						Children: SubpartChildren{
							&SubjectGroup{
								Type: "SUBJGRP",
								Header: XMLString{
									Content: "Assignment of Rights to Benefits",
								},
								Citation: SectionCitation{"ECFRb511534bf191cab"},
								Children: SubjectGroupChildren{
									&Section{
										Type: "SECTION",
										Citation: SectionCitation{"433", "145"},
										Header: "§ 433.145 Assignment of rights to benefits - State plan requirements.",
										Children: SectionChildren{
											&Paragraph{
												Type: "Paragraph",
												Content: "(a) A State plan must provide that, as a condition of eligibility, each legally...",
											},
											&Paragraph{
												Type: "Paragraph",
												Content: "(1) Assign to the Medicaid agency his or her rights, or the rights of any other...",
											},
										},
									},
								},
							},
						},
					},
					&Section{
						Type: "SECTION",
						Citation: SectionCitation{"433", "146"},
						Header: "§ 433.146 Rights assigned; assignment method.",
						Children: SectionChildren{
							&Paragraph{
								Type: "Paragraph",
								Content: "(a) Except as specified in paragraph (b) of this section, the agency must require...",
							},
						},
					},
				},
			},
			Error: false,
		},
		{
			Name: "test-invalid-part",
			Input: []byte(`
				<DIV8 N="433.146" TYPE="SECTION" VOLUME="4">
					<HEAD>§ 433.146 Rights assigned; assignment method.</HEAD>
					<P>(a) Except as specified in paragraph (b) of this section, the agency must require...</P>
				</DIV8>
			`),
			Expected: Part{},
			Error: true,
		},
		{
			Name: "test-bad-xml",
			Input: []byte("<PThis is bad XML"),
			Expected: Part{},
			Error: true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			reader := bytes.NewReader(tc.Input)
			out, err := ParsePart(reader)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received (%+v)", out)
			} else if err == nil && !reflect.DeepEqual(out, &tc.Expected) {
				t.Errorf("expected (%+v), received (%+v)", tc.Expected, out)
			}
		})
	}
}

func TestPartPostProcess(t *testing.T) {
	input := Part{
		XMLName: xml.Name{
			Space: "",
			Local: "DIV5",
		},
		Citation: SectionCitation{"some", "part"},
		Type: "PART",
		Header: "Some header",
		Children: PartChildren{
			&Subpart{
				Header: "Some subpart",
				Citation: SectionCitation{"A"},
				Type: "SUBPART",
				Children: SubpartChildren{
					&Section{
						Type: "SECTION",
						Citation: SectionCitation{"433", "11"},
						Header: "§ 433.11 Enhanced FMAP rate for children.",
						Children: SectionChildren{
							&Paragraph{
								Type: "Paragraph",
								Content: "(a) Subject to the conditions in paragraph (b) of this section, the enhanced...",
							},
						},
					},
				},
			},
		},
	}

	expected := Part{
		XMLName: xml.Name{
			Space: "",
			Local: "DIV5",
		},
		Citation: SectionCitation{"some", "part"},
		Type: "PART",
		Header: "Some header",
		Children: PartChildren{
			&Subpart{
				Header: "Some subpart",
				Citation: SectionCitation{"A"},
				Type: "SUBPART",
				Children: SubpartChildren{
					&Section{
						Type: "SECTION",
						Citation: SectionCitation{"433", "11"},
						Header: "§ 433.11 Enhanced FMAP rate for children.",
						Children: SectionChildren{
							&Paragraph{
								Type: "Paragraph",
								Content: "(a) Subject to the conditions in paragraph (b) of this section, the enhanced...",
								Citation: []string{"433", "11", "a"},
								Marker: []string{"a"},
							},
						},
					},
				},
			},
		},
	}

	err := input.PostProcess()
	if err != nil {
		t.Errorf("PostProcess failed, this should not happen")
	} else if !reflect.DeepEqual(input, expected) {
		t.Errorf("expected (%+v), received (%+v)", expected, input)
	}
}

func TestPartChildrenUnmarshalXML(t *testing.T) {
	testTable := []struct {
		Name string
		Input []byte
		Expected PartChildren
		Error bool
	}{
		{
			Name: "test-subpart",
			Input: []byte(`
				<DIV6 N="L" TYPE="SUBPART">
					<HEAD>Subpart L - Step, Handhold, and Deck Requirements...</HEAD>
					<DIV7 N="ECFRb511534bf191cab" TYPE="SUBJGRP">
						<HEAD>Assignment of Rights to Benefits</HEAD>
						<DIV8 N="433.145" TYPE="SECTION" VOLUME="4">
							<HEAD>§ 433.145 Assignment of rights to benefits - State plan requirements.</HEAD>
							<P>(a) A State plan must provide that, as a condition of eligibility, each legally...</P>
							<P>(1) Assign to the Medicaid agency his or her rights, or the rights of any other...</P>
						</DIV8>
					</DIV7>
					<DIV8 N="433.146" TYPE="SECTION" VOLUME="4">
						<HEAD>§ 433.146 Rights assigned; assignment method.</HEAD>
						<P>(a) Except as specified in paragraph (b) of this section, the agency must require...</P>
					</DIV8>
				</DIV6>
			`),
			Expected: PartChildren{
				&Subpart{
					Type: "SUBPART",
					Citation: SectionCitation{"L"},
					Header: "Subpart L - Step, Handhold, and Deck Requirements...",
					Children: SubpartChildren{
						&SubjectGroup{
							Type: "SUBJGRP",
							Header: XMLString{
								Content: "Assignment of Rights to Benefits",
							},
							Citation: SectionCitation{"ECFRb511534bf191cab"},
							Children: SubjectGroupChildren{
								&Section{
									Type: "SECTION",
									Citation: SectionCitation{"433", "145"},
									Header: "§ 433.145 Assignment of rights to benefits - State plan requirements.",
									Children: SectionChildren{
										&Paragraph{
											Type: "Paragraph",
											Content: "(a) A State plan must provide that, as a condition of eligibility, each legally...",
										},
										&Paragraph{
											Type: "Paragraph",
											Content: "(1) Assign to the Medicaid agency his or her rights, or the rights of any other...",
										},
									},
								},
							},
						},
						&Section{
							Type: "SECTION",
							Citation: SectionCitation{"433", "146"},
							Header: "§ 433.146 Rights assigned; assignment method.",
							Children: SectionChildren{
								&Paragraph{
									Type: "Paragraph",
									Content: "(a) Except as specified in paragraph (b) of this section, the agency must require...",
								},
							},
						},
					},
				},
			},
			Error: false,
		},
		{
			Name: "test-section",
			Input: []byte(`
				<DIV8 N="399.201" TYPE="SECTION" VOLUME="5">
					<HEAD>§ 399.201 Purpose and scope.</HEAD>
					<P>This subpart prescribes step, handhold, and deck requirements on...</P>
				</DIV8>
			`),
			Expected: PartChildren{
				&Section{
					Type: "SECTION",
					Citation: SectionCitation{"399", "201"},
					Header: "§ 399.201 Purpose and scope.",
					Children: SectionChildren{
						&Paragraph{
							Type: "Paragraph",
							Content: "This subpart prescribes step, handhold, and deck requirements on...",
						},
					},
				},
			},
			Error: false,
		},
		{
			Name: "test-unknown-type",
			Input: []byte("<UNKNOWN>This is an unknown type</UNKNOWN>"),
			Expected: nil,
			Error: false,
		},
		{
			Name: "test-bad-xml",
			Input: []byte("<BADXML>This is bad XML</"),
			Expected: nil,
			Error: true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			reader := bytes.NewReader(tc.Input)
			d := xml.NewDecoder(reader)
			var pc PartChildren
			err := d.Decode(&pc)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received (%+v)", pc)
			} else if err == nil && !reflect.DeepEqual(pc, tc.Expected) {
				t.Errorf("expected (%+v), received (%+v)", tc.Expected, pc)
			}
		})
	}
}

func TestSubpartPostProcess(t *testing.T) {
	input := Subpart{
		Header: "Some subpart",
		Citation: SectionCitation{"A"},
		Type: "SUBPART",
		Children: SubpartChildren{
			&Section{
				Type: "SECTION",
				Citation: SectionCitation{"433", "11"},
				Header: "§ 433.11 Enhanced FMAP rate for children.",
				Children: SectionChildren{
					&Paragraph{
						Type: "Paragraph",
						Content: "(a) Subject to the conditions in paragraph (b) of this section, the enhanced...",
					},
				},
			},
		},
	}

	expected := Subpart{
		Header: "Some subpart",
		Citation: SectionCitation{"A"},
		Type: "SUBPART",
		Children: SubpartChildren{
			&Section{
				Type: "SECTION",
				Citation: SectionCitation{"433", "11"},
				Header: "§ 433.11 Enhanced FMAP rate for children.",
				Children: SectionChildren{
					&Paragraph{
						Type: "Paragraph",
						Content: "(a) Subject to the conditions in paragraph (b) of this section, the enhanced...",
						Citation: []string{"433", "11", "a"},
						Marker: []string{"a"},
					},
				},
			},
		},
	}

	err := input.PostProcess()
	if err != nil {
		t.Errorf("PostProcess failed, this should not happen")
	} else if !reflect.DeepEqual(input, expected) {
		t.Errorf("expected (%+v), received (%+v)", expected, input)
	}	
}

func TestSubpartChildrenUnmarshalXML(t *testing.T) {
	testTable := []struct {
		Name string
		Input []byte
		Expected SubpartChildren
		Error bool
	}{
		{
			Name: "test-section",
			Input: []byte(`
				<DIV8 N="399.201" TYPE="SECTION" VOLUME="5">
					<HEAD>§ 399.201 Purpose and scope.</HEAD>
					<P>This subpart prescribes step, handhold, and deck requirements on...</P>
				</DIV8>
			`),
			Expected: SubpartChildren{
				&Section{
					Type: "SECTION",
					Citation: SectionCitation{"399", "201"},
					Header: "§ 399.201 Purpose and scope.",
					Children: SectionChildren{
						&Paragraph{
							Type: "Paragraph",
							Content: "This subpart prescribes step, handhold, and deck requirements on...",
						},
					},
				},
			},
			Error: false,
		},
		{
			Name: "test-subject-group",
			Input: []byte(`
				<DIV7 N="ECFRb511534bf191cab" TYPE="SUBJGRP">
					<HEAD>Assignment of Rights to Benefits</HEAD>
					<DIV8 N="433.145" TYPE="SECTION" VOLUME="4">
						<HEAD>§ 433.145 Assignment of rights to benefits - State plan requirements.</HEAD>
						<P>(a) A State plan must provide that, as a condition of eligibility, each legally...</P>
						<P>(1) Assign to the Medicaid agency his or her rights, or the rights of any other...</P>
					</DIV8>
					<DIV8 N="433.146" TYPE="SECTION" VOLUME="4">
						<HEAD>§ 433.146 Rights assigned; assignment method.</HEAD>
						<P>(a) Except as specified in paragraph (b) of this section, the agency must require...</P>
					</DIV8>
				</DIV7>
			`),
			Expected: SubpartChildren{
				&SubjectGroup{
					Type: "SUBJGRP",
					Header: XMLString{
						Content: "Assignment of Rights to Benefits",
					},
					Citation: SectionCitation{"ECFRb511534bf191cab"},
					Children: SubjectGroupChildren{
						&Section{
							Type: "SECTION",
							Citation: SectionCitation{"433", "145"},
							Header: "§ 433.145 Assignment of rights to benefits - State plan requirements.",
							Children: SectionChildren{
								&Paragraph{
									Type: "Paragraph",
									Content: "(a) A State plan must provide that, as a condition of eligibility, each legally...",
								},
								&Paragraph{
									Type: "Paragraph",
									Content: "(1) Assign to the Medicaid agency his or her rights, or the rights of any other...",
								},
							},
						},
						&Section{
							Type: "SECTION",
							Citation: SectionCitation{"433", "146"},
							Header: "§ 433.146 Rights assigned; assignment method.",
							Children: SectionChildren{
								&Paragraph{
									Type: "Paragraph",
									Content: "(a) Except as specified in paragraph (b) of this section, the agency must require...",
								},
							},
						},
					},
				},
			},
			Error: false,
		},
		{
			Name: "test-appendix",
			Input: []byte(`
				<DIV9 N="Appendix A to Subchapter B of Chapter III" TYPE="APPENDIX" VOLUME="5">
					<HEAD>Appendix A to Subchapter B of Chapter III [Reserved]</HEAD>
					<P>This appendix describes the...</P>
				</DIV9>
			`),
			Expected: SubpartChildren{
				&Appendix{
					Type: "APPENDIX",
					Citation: AppendixCitation{"Appendix", "A", "to", "Subchapter", "B", "of", "Chapter", "III"},
					Header: "Appendix A to Subchapter B of Chapter III [Reserved]",
					Children: AppendixChildren{
						&Paragraph{
							Type: "Paragraph",
							Content: "This appendix describes the...",
						},
					},
				},
			},
			Error: false,
		},
		{
			Name: "test-source",
			Input: []byte(`
				<SOURCE>
					<HED>Source:</HED>
					<PSPACE>44 FR 43732, July 26, 1979, unless otherwise noted.</PSPACE>
				</SOURCE>
			`),
			Expected: SubpartChildren{
				&Source{
					Type: "Source",
					Header: "Source:",
					Content: "44 FR 43732, July 26, 1979, unless otherwise noted.",
				},
			},
			Error: false,
		},
		{
			Name: "test-unknown-type",
			Input: []byte("<UNKNOWN>This is an unknown type</UNKNOWN>"),
			Expected: nil,
			Error: false,
		},
		{
			Name: "test-bad-xml",
			Input: []byte("<BADXML>This is bad XML</"),
			Expected: nil,
			Error: true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			reader := bytes.NewReader(tc.Input)
			d := xml.NewDecoder(reader)
			var sc SubpartChildren
			err := d.Decode(&sc)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received (%+v)", sc)
			} else if err == nil && !reflect.DeepEqual(sc, tc.Expected) {
				t.Errorf("expected (%+v), received (%+v)", tc.Expected, sc)
			}
		})
	}
}

func TestXMLStringMarshalText(t *testing.T) {
	input := XMLString{
		Content: "This is some XML bytes",
	}
	expected := []byte("This is some XML bytes")
	output, _ := input.MarshalText()
	if !reflect.DeepEqual(expected, output) {
		t.Errorf("expected (%s), received (%s)", expected, output)
	}
}

func TestSubjectGroupPostProcess(t *testing.T) {
	input := SubjectGroup{
		Type: "SUBJGRP",
		Header: XMLString{
			Content: "Some subject group",
		},
		Citation: SectionCitation{"some", "subject", "group"},
		Children: SubjectGroupChildren{
			&Section{
				Type: "SECTION",
				Citation: SectionCitation{"433", "11"},
				Header: "§ 433.11 Enhanced FMAP rate for children.",
				Children: SectionChildren{
					&Paragraph{
						Type: "Paragraph",
						Content: "(a) Subject to the conditions in paragraph (b) of this section, the enhanced...",
					},
				},
			},		
		},
	}

	expected := SubjectGroup{
		Type: "SUBJGRP",
		Header: XMLString{
			Content: "Some subject group",
		},
		Citation: SectionCitation{"some", "subject", "group"},
		Children: SubjectGroupChildren{
			&Section{
				Type: "SECTION",
				Citation: SectionCitation{"433", "11"},
				Header: "§ 433.11 Enhanced FMAP rate for children.",
				Children: SectionChildren{
					&Paragraph{
						Type: "Paragraph",
						Content: "(a) Subject to the conditions in paragraph (b) of this section, the enhanced...",
						Citation: []string{"433", "11", "a"},
						Marker: []string{"a"},
					},
				},
			},		
		},
	}

	err := input.PostProcess()
	if err != nil {
		t.Errorf("PostProcess failed, this should not happen")
	} else if !reflect.DeepEqual(input, expected) {
		t.Errorf("expected (%+v), received (%+v)", expected, input)
	}
}

func TestSubjectGroupChildrenUnmarshalXML(t *testing.T) {
	testTable := []struct {
		Name string
		Input []byte
		Expected SubjectGroupChildren
		Error bool
	}{
		{
			Name: "test-section",
			Input: []byte(`
				<DIV8 N="399.201" TYPE="SECTION" VOLUME="5">
					<HEAD>§ 399.201 Purpose and scope.</HEAD>
					<P>This subpart prescribes step, handhold, and deck requirements on...</P>
				</DIV8>
			`),
			Expected: SubjectGroupChildren{
				&Section{
					Type: "SECTION",
					Citation: SectionCitation{"399", "201"},
					Header: "§ 399.201 Purpose and scope.",
					Children: SectionChildren{
						&Paragraph{
							Type: "Paragraph",
							Content: "This subpart prescribes step, handhold, and deck requirements on...",
						},
					},
				},
			},
			Error: false,
		},
		{
			Name: "test-footnote",
			Input: []byte("<FTNT>This is a footnote</FTNT>"),
			Expected: SubjectGroupChildren{
				&FootNote{
					Type: "FootNote",
					Content: "This is a footnote",
				},
			},
			Error: false,
		},
		{
			Name: "test-unknown-type",
			Input: []byte("<UNKNOWN>This is an unknown type</UNKNOWN>"),
			Expected: nil,
			Error: false,
		},
		{
			Name: "test-bad-xml",
			Input: []byte("<BADXML>This is bad XML</"),
			Expected: nil,
			Error: true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			reader := bytes.NewReader(tc.Input)
			d := xml.NewDecoder(reader)
			var sjc SubjectGroupChildren
			err := d.Decode(&sjc)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received (%+v)", sjc)
			} else if err == nil && !reflect.DeepEqual(sjc, tc.Expected) {
				t.Errorf("expected (%+v), received (%+v)", tc.Expected, sjc)
			}
		})
	}
}

func TestSectionPostProcess(t *testing.T) {
	testTable := []struct {
		Name string
		Input Section
		Expected Section
		Error bool
	}{
		{
			Name: "test-full-valid-section",
			Input: Section{
				Type: "SECTION",
				Citation: SectionCitation{"433", "11"},
				Header: "§ 433.11 Enhanced FMAP rate for children.",
				Children: SectionChildren{
					&Paragraph{
						Type: "Paragraph",
						Content: "(a) Subject to the conditions in paragraph (b) of this section, the enhanced...",
					},
					&Paragraph{
						Type: "Paragraph",
						Content: "(1) Services provided to optional targeted low-income children described in § 435...",
					},
					&Paragraph{
						Type: "Paragraph",
						Content: "(2) Services provided to children born before October 1, 1983, with or without...",
					},
					&Paragraph{
						Type: "Paragraph",
						Content: "(i) They had been born on or after that date; and ",
					},
					&Paragraph{
						Type: "Paragraph",
						Content: "(ii) They would not qualify for medical assistance under the State plan in effect...",
					},
					&Paragraph{
						Type: "Paragraph",
						Content: "(b) Enhanced FMAP is not available if - ",
					},
					&Paragraph{
						Type: "Paragraph",
						Content: "(1) A State adopts income and resource standards and methodologies for purposes of...",
					},
					&Paragraph{
						Type: "Paragraph",
						Content: "(2) No funds are available in the State's title XXI allotment, as determined under...",
					},
					&Paragraph{
						Type: "Paragraph",
						Content: "(3) The State fails to maintain a valid method of identifying services provided on...",
					},
					&Citation{
						Type: "Citation",
						Content: "[66 FR 2666, Jan. 11, 2001] ",
					},
				},
			},
			Expected: Section{
				Type: "SECTION",
				Citation: SectionCitation{"433", "11"},
				Header: "§ 433.11 Enhanced FMAP rate for children.",
				Children: SectionChildren{
					&Paragraph{
						Type: "Paragraph",
						Content: "(a) Subject to the conditions in paragraph (b) of this section, the enhanced...",
						Citation: []string{"433", "11", "a"},
						Marker: []string{"a"},
					},
					&Paragraph{
						Type: "Paragraph",
						Content: "(1) Services provided to optional targeted low-income children described in § 435...",
						Citation: []string{"433", "11", "a", "1"},
						Marker: []string{"1"},
					},
					&Paragraph{
						Type: "Paragraph",
						Content: "(2) Services provided to children born before October 1, 1983, with or without...",
						Citation: []string{"433", "11", "a", "2"},
						Marker: []string{"2"},
					},
					&Paragraph{
						Type: "Paragraph",
						Content: "(i) They had been born on or after that date; and ",
						Citation: []string{"433", "11", "a", "2", "i"},
						Marker: []string{"i"},
					},
					&Paragraph{
						Type: "Paragraph",
						Content: "(ii) They would not qualify for medical assistance under the State plan in effect...",
						Citation: []string{"433", "11", "a", "2", "ii"},
						Marker: []string{"ii"},
					},
					&Paragraph{
						Type: "Paragraph",
						Content: "(b) Enhanced FMAP is not available if - ",
						Citation: []string{"433", "11", "b"},
						Marker: []string{"b"},
					},
					&Paragraph{
						Type: "Paragraph",
						Content: "(1) A State adopts income and resource standards and methodologies for purposes of...",
						Citation: []string{"433", "11", "b", "1"},
						Marker: []string{"1"},
					},
					&Paragraph{
						Type: "Paragraph",
						Content: "(2) No funds are available in the State's title XXI allotment, as determined under...",
						Citation: []string{"433", "11", "b", "2"},
						Marker: []string{"2"},
					},
					&Paragraph{
						Type: "Paragraph",
						Content: "(3) The State fails to maintain a valid method of identifying services provided on...",
						Citation: []string{"433", "11", "b", "3"},
						Marker: []string{"3"},
					},
					&Citation{
						Type: "Citation",
						Content: "[66 FR 2666, Jan. 11, 2001] ",
					},
				},
			},
			Error: false,
		},
		{
			Name: "test-md5-hash-citation",
			Input: Section{
				Type: "SECTION",
				Citation: SectionCitation{"432", "1"},
				Header: "§ 432.1 Basis and purpose.",
				Children: SectionChildren{
					&Paragraph{
						Type: "Paragraph",
						Content: "This part prescribes regulations to implement section 1902(a)(4) of the Act, which relates to a merit system of State personnel administration and training and use of subprofessional staff and volunteers in State Medicaid programs, and section 1903(a), rates of FFP for Medicaid staffing and training costs. It also prescribes regulations, based on the general administrative authority in section 1902(a)(4), for State training programs for all staff. ",
					},
				},
			},
			Expected: Section{
				Type: "SECTION",
				Citation: SectionCitation{"432", "1"},
				Header: "§ 432.1 Basis and purpose.",
				Children: SectionChildren{
					&Paragraph{
						Type: "Paragraph",
						Content: "This part prescribes regulations to implement section 1902(a)(4) of the Act, which relates to a merit system of State personnel administration and training and use of subprofessional staff and volunteers in State Medicaid programs, and section 1903(a), rates of FFP for Medicaid staffing and training costs. It also prescribes regulations, based on the general administrative authority in section 1902(a)(4), for State training programs for all staff. ",
						Citation: []string{"432", "1", "a9b4ca164fc8bf23d8d44767a9940bf2"},
						Marker: nil,
					},
				},
			},
			Error: false,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			err := tc.Input.PostProcess()
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received (%+v)", tc.Input)
			} else if err == nil && !reflect.DeepEqual(tc.Input, tc.Expected) {
				t.Errorf("expected (%+v), received (%+v)", tc.Expected, tc.Input)
			}
		})
	}
}

func TestSectionChildrenUnmarshalXML(t *testing.T) {
	testTable := []struct {
		Name string
		Input []byte
		Expected SectionChildren
		Error bool
	}{
		{
			Name: "test-paragraph",
			Input: []byte(`
				<P>This is a paragraph</P>
			`),
			Expected: SectionChildren{
				&Paragraph{
					Type: "Paragraph",
					Content: "This is a paragraph",
				},
			},
			Error: false,
		},
		{
			Name: "test-flush-paragraph",
			Input: []byte("<FP>This is a flush paragraph</FP>"),
			Expected: SectionChildren{
				&FlushParagraph{
					Type: "FlushParagraph",
					Content: "This is a flush paragraph",
				},
			},
			Error: false,
		},
		{
			Name: "test-flush-paragraph-1",
			Input: []byte("<FP-1>This is a flush paragraph (1)</FP-1>"),
			Expected: SectionChildren{
				&FlushParagraph{
					Type: "FlushParagraph",
					Content: "This is a flush paragraph (1)",
				},
			},
			Error: false,
		},
		{
			Name: "test-flush-paragraph-2",
			Input: []byte("<FP-2>This is a flush paragraph (2)</FP-2>"),
			Expected: SectionChildren{
				&FlushParagraph{
					Type: "FlushParagraph",
					Content: "This is a flush paragraph (2)",
				},
			},
			Error: false,
		},
		{
			Name: "test-image",
			Input: []byte("<img src=\"images/test.png\" />"),
			Expected: SectionChildren{
				&Image{
					Type: "Image",
					Source: "images/test.png",
				},
			},
			Error: false,
		},
		{
			Name: "test-extract",
			Input: []byte("<EXTRACT>This is an extract</EXTRACT>"),
			Expected: SectionChildren{
				&Extract{
					Type: "Extract",
					Content: "This is an extract",
				},
			},
			Error: false,
		},
		{
			Name: "test-citation",
			Input: []byte("<CITA TYPE=\"N\">This is a citation</CITA>"),
			Expected: SectionChildren{
				&Citation{
					Type: "Citation",
					Content: "This is a citation",
				},
			},
			Error: false,
		},
		{
			Name: "test-section-authority",
			Input: []byte("<SECAUTH TYPE=\"N\">This is a section authority</SECAUTH>"),
			Expected: SectionChildren{
				&SectionAuthority{
					Type: "SectionAuthority",
					Content: "This is a section authority",
				},
			},
			Error: false,
		},
		{
			Name: "test-footnote",
			Input: []byte("<FTNT>This is a footnote</FTNT>"),
			Expected: SectionChildren{
				&FootNote{
					Type: "FootNote",
					Content: "This is a footnote",
				},
			},
			Error: false,
		},
		{
			Name: "test-division",
			Input: []byte("<DIV>This is a division</DIV>"),
			Expected: SectionChildren{
				&Division{
					Type: "Division",
					Content: "This is a division",
				},
			},
			Error: false,
		},
		{
			Name: "test-effective-date-note",
			Input: []byte(`
				<EFFDNOT>
					<HED>Effective Date Note:</HED>
					<PSPACE>This is an effective date note</PSPACE>
				</EFFDNOT>
			`),
			Expected: SectionChildren{
				&EffectiveDateNote{
					Type: "EffectiveDateNote",
					Header: "Effective Date Note:",
					Content: "This is an effective date note",
				},
			},
			Error: false,
		},
		{
			Name: "test-unknown-type",
			Input: []byte("<UNKNOWN>This is an unknown type</UNKNOWN>"),
			Expected: nil,
			Error: false,
		},
		{
			Name: "test-bad-xml",
			Input: []byte("<BADXML>This is bad XML</"),
			Expected: nil,
			Error: true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			reader := bytes.NewReader(tc.Input)
			d := xml.NewDecoder(reader)
			var sc SectionChildren
			err := d.Decode(&sc)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received (%+v)", sc)
			} else if err == nil && !reflect.DeepEqual(sc, tc.Expected) {
				t.Errorf("expected (%+v), received (%+v)", tc.Expected, sc)
			}
		})
	}
}

func TestSectionCitationUnmarshalText(t *testing.T) {
	testTable := []struct {
		Name string
		Input []byte
		Expected SectionCitation
	}{
		{
			Name: "test-part",
			Input: []byte("430"),
			Expected: SectionCitation{"430"},
		},
		{
			Name: "test-subpart",
			Input: []byte("A"),
			Expected: SectionCitation{"A"},
		},
		{
			Name: "test-subject-group",
			Input: []byte("ECFR14123c518724401"),
			Expected: SectionCitation{"ECFR14123c518724401"},
		},
		{
			Name: "test-section",
			Input: []byte("430.1"),
			Expected: SectionCitation{"430", "1"},
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			var output SectionCitation
			output.UnmarshalText(tc.Input)
			if !reflect.DeepEqual(output, tc.Expected) {
				t.Errorf("expected (%+v), received (%+v)", tc.Expected, output)
			}
		})
	}	
}

func TestAppendixChildrenUnmarshalXML(t *testing.T) {
	testTable := []struct {
		Name string
		Input []byte
		Expected AppendixChildren
		Error bool
	}{
		{
			Name: "test-paragraph",
			Input: []byte("<P>This is a paragraph</P>"),
			Expected: AppendixChildren{
				&Paragraph{
					Type: "Paragraph",
					Content: "This is a paragraph",
				},
			},
			Error: false,
		},
		{
			Name: "test-heading",
			Input: []byte("<HD1>This is a heading</HD1>"),
			Expected: AppendixChildren{
				&Heading{
					Type: "Heading",
					Content: "This is a heading",
				},
			},
			Error: false,
		},
		{
			Name: "test-unknown-type",
			Input: []byte("<UNKNOWN>This is an unknown type</UNKNOWN>"),
			Expected: nil,
			Error: false,
		},
		{
			Name: "test-bad-xml",
			Input: []byte("<BADXML>This is bad XML</"),
			Expected: nil,
			Error: true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			reader := bytes.NewReader(tc.Input)
			d := xml.NewDecoder(reader)
			var ac AppendixChildren
			err := d.Decode(&ac)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received (%+v)", ac)
			} else if err == nil && !reflect.DeepEqual(ac, tc.Expected) {
				t.Errorf("expected (%+v), received (%+v)", tc.Expected, ac)
			}
		})
	}
}

func TestAppendixCitationUnmarshalText(t *testing.T) {
	input := []byte("Appendix A to Subchapter B of Chapter III")
	expected := AppendixCitation{"Appendix", "A", "to", "Subchapter", "B", "of", "Chapter", "III"}
	var output AppendixCitation
	output.UnmarshalText(input)
	if !reflect.DeepEqual(output, expected) {
		t.Errorf("expected (%+v), received (%+v)", expected, output)
	}
}

//TO IMPLEMENT
func TestParagraphLevel(t *testing.T) {
	
}
