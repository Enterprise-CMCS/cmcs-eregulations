package ecfr

import (
	"testing"
	"net/http/httptest"
	"net/http"
	"context"
	"time"

	"github.com/go-test/deep"
)

func TestRangeStringUnmarshal(t *testing.T) {
	testTable := []struct{
		Name string
		Input []byte
		Expected RangeString
	}{
		{
			Name: "test-range-string",
			Input: []byte("432.1 – 432.200"),
			Expected: RangeString{"432.1", "432.200"},
		},
		{
			Name: "test-array-input",
			Input: []byte("[\"432.1\", \"432.200\"]"),
			Expected: RangeString{"432.1", "432.200"},
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			var rs RangeString
			rs.UnmarshalJSON(tc.Input)
			if diff := deep.Equal(rs, tc.Expected); diff != nil {
				t.Errorf("output not as expected: %+v", diff)
			}
		})
	}
}

func TestHTMLStringUnmarshal(t *testing.T) {
	input := []byte("&quot;Hello world&quot; &lt;&amp; &#39;")
	expected := HTMLString("\"Hello world\" <& '")
	var hs HTMLString
	hs.UnmarshalText(input)
	if hs != expected {
		t.Errorf("expected (%s), received (%s)", expected, hs)
	}
}

func TestIdentifierStringUnmarshal(t *testing.T) {
	testTable := []struct {
		Name string
		Input []byte
		Expected IdentifierString
	}{
		{
			Name: "test-title-identifier",
			Input: []byte("42"),
			Expected: IdentifierString{"42"},
		},
		{
			Name: "test-chapter-identifier",
			Input: []byte("IV"),
			Expected: IdentifierString{"IV"},
		},
		{
			Name: "test-subchapter-identifier",
			Input: []byte("C"),
			Expected: IdentifierString{"C"},
		},
		{
			Name: "test-part-identifier",
			Input: []byte("430"),
			Expected: IdentifierString{"430"},
		},
		{
			Name: "test-subpart-identifier",
			Input: []byte("A"),
			Expected: IdentifierString{"A"},
		},
		{
			Name: "test-subjectgroup-identifier",
			Input: []byte("ECFR370de681c5a0a70"),
			Expected: IdentifierString{"ECFR370de681c5a0a70"},
		},
		{
			Name: "test-section-identifier",
			Input: []byte("430.1"),
			Expected: IdentifierString{"430", "1"},
		},
		{
			Name: "test-paragraph-identifier",
			Input: []byte("430.1 a 1"),
			Expected: IdentifierString{"430", "1", "a", "1"},
		},
		{
			Name: "test-array-input",
			Input: []byte("[\"430\", \"12\"]"),
			Expected: IdentifierString{"430", "12"},
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			var is IdentifierString
			is.UnmarshalJSON(tc.Input)
			if diff := deep.Equal(is, tc.Expected); diff != nil {
				t.Errorf("output not as expected: %+v", diff)
			}
		})
	}
}

func TestSubchapterParts(t *testing.T) {
	testTable := []struct {
		Name string
		Input Structure
		Expected []*Structure
		Error bool
	}{
		{
			Name: "test-one-level",
			Input: Structure{
				Children: []*Structure{},
			},
			Expected: []*Structure{},
			Error: true,
		},
		{
			Name: "test-two-levels",
			Input: Structure{
				Children: []*Structure{
					&Structure{
						Children: []*Structure{},
					},
				},
			},
			Expected: []*Structure{},
			Error: true,
		},
		{
			Name: "test-three-levels",
			Input: Structure{
				Children: []*Structure{
					&Structure{
						Children: []*Structure{
							&Structure{
								Children: []*Structure{
									&Structure{
										LabelDescription: "test 1",
									},
									&Structure{
										LabelDescription: "test 2",
									},
									&Structure{
										LabelDescription: "test 3",
									},
								},
							},
						},
					},
				},
			},
			Expected: []*Structure{
				&Structure{
					LabelDescription: "test 1",
				},
				&Structure{
					LabelDescription: "test 2",
				},
				&Structure{
					LabelDescription: "test 3",
				},
			},
			Error: false,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			out, err := SubchapterParts(&tc.Input)
			diff := deep.Equal(out, tc.Expected)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received (%+v)", out)
			} else if err == nil && diff != nil {
				t.Errorf("output not as expected: %+v", diff)
			}
		})
	}
}

func TestExtractSubchapterParts(t *testing.T) {
	testTable := []struct {
		Name string
		Server *httptest.Server
		Expected []string
		Error bool
	}{
		{
			Name: "test-valid-response",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusOK)
				w.Write([]byte(`{
					"identifier": "42",
					"label": "Title 42 - Public Health",
					"label_level": "Title 42",
					"label_description": "Public Health",
					"reserved": false,
					"type": "title",
					"children": [
						{
							"identifier": "IV",
							"label": " Chapter IV - Centers for Medicare &amp; Medicaid Services, Department of Health and Human Services",
							"label_level": " Chapter IV",
							"label_description": "Centers for Medicare &amp; Medicaid Services, Department of Health and Human Services",
							"reserved": false,
							"type": "chapter",
							"children": [
								{
									"identifier": "C",
									"label": "Subchapter C - Medical Assistance Programs",
									"label_level": "Subchapter C",
									"label_description": "Medical Assistance Programs",
									"reserved": false,
									"type": "subchapter",
									"children": [
										{
											"identifier": "430",
											"label": "Part 430 - Grants to States for Medical Assistance Programs",
											"label_level": "Part 430",
											"label_description": "Grants to States for Medical Assistance Programs",
											"reserved": false,
											"type": "part",
											"volumes": [
												"4"
											],
											"children": [],
											"descendant_range": "430.0 – 430.104"
										},
										{
											"identifier": "431",
											"label": "Part 431 - State Organization and General Administration",
											"label_level": "Part 431",
											"label_description": "State Organization and General Administration",
											"reserved": false,
											"type": "part",
											"volumes": [
												"4"
											],
											"children": [],
											"descendant_range": "431.1 – 431.1010"
										},
										{
											"identifier": "432",
											"label": "Part 432 - State Personnel Administration",
											"label_level": "Part 432",
											"label_description": "State Personnel Administration",
											"reserved": false,
											"type": "part",
											"volumes": [
												"4"
											],
											"children": [],
											"descendant_range": "432.1 – 432.55"
										}
									],
									"descendant_range": "430 – 456"
								}
							],
							"descendant_range": "400 – 699"
						}
					]
				}`))
			})),
			Expected: []string{"430", "431", "432"},
			Error: false,
		},
		{
			Name: "test-server-error",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusInternalServerError)
				w.Write([]byte(`{ "exception": "All is well" }`))
			})),
			Expected: []string{},
			Error: true,
		},
		{
			Name: "test-bad-json",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusOK)
				w.Write([]byte(`{ "what" "this json won't decode properly"`))
			})),
			Expected: []string{},
			Error: true,
		},
		{
			Name: "test-bad-depth",
			Server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusOK)
				w.Write([]byte(`{
					"identifier": "42",
					"label": "Title 42 - Public Health",
					"label_level": "Title 42",
					"label_description": "Public Health",
					"reserved": false,
					"type": "title",
					"children": [
						{
							"identifier": "IV",
							"label": " Chapter IV - Centers for Medicare &amp; Medicaid Services, Department of Health and Human Services",
							"label_level": " Chapter IV",
							"label_description": "Centers for Medicare &amp; Medicaid Services, Department of Health and Human Services",
							"reserved": false,
							"type": "chapter",
							"children": [],
							"descendant_range": "400 – 699"
						}
					]
				}`))
			})),
			Expected: []string{},
			Error: true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			defer tc.Server.Close()
			EcfrSite = tc.Server.URL
			ctx, cancel := context.WithTimeout(context.Background(), 1 * time.Second)
			defer cancel()
			subchapter := SubchapterOption{
				Chapter: "IV",
				Subchapter: "C",
			}

			out, err := ExtractSubchapterParts(ctx, time.Now(), 42, &subchapter)

			diff := deep.Equal(out, tc.Expected)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received (%+v)", out)
			} else if err == nil && diff != nil {
				t.Errorf("output not as expected: %+v", diff)
			}
		})
	}
}

func TestDeterminePartDepth(t *testing.T) {
	testTable := []struct{
		Name string
		Structure Structure
		Part string
		Depth int
	}{
		{
			Name: "test-level-zero",
			Structure: Structure{
				Identifier: IdentifierString{"433"},
				Children: []*Structure{},
				Type: "part",
			},
			Part: "433",
			Depth: 0,
		},
		{
			Name: "test-level-3",
			Structure: Structure{
				Identifier: IdentifierString{"42"},
				Type: "title",
				Children: []*Structure{
					&Structure{
						Identifier: IdentifierString{"IV"},
						Type: "chapter",
						Children: []*Structure{
							&Structure{
								Identifier: IdentifierString{"C"},
								Type: "subchapter",
								Children: []*Structure{
									&Structure{
										Identifier: IdentifierString{"433"},
										Type: "part",
										Children: []*Structure{},
									},
								},
							},
						},
					},
				},
			},
			Part: "433",
			Depth: 3,
		},
		{
			Name: "test-multiple-children",
			Structure: Structure{
				Identifier: IdentifierString{"42"},
				Type: "title",
				Children: []*Structure{
					&Structure{
						Identifier: IdentifierString{"440"},
						Type: "part",
						Children: []*Structure{},
					},
					&Structure{
						Identifier: IdentifierString{"IV"},
						Type: "chapter",
						Children: []*Structure{
							&Structure{
								Identifier: IdentifierString{"C"},
								Type: "subchapter",
								Children: []*Structure{
									&Structure{
										Identifier: IdentifierString{"200"},
										Type: "part",
										Children: []*Structure{},
									},
									&Structure{
										Identifier: IdentifierString{"300"},
										Type: "part",
										Children: []*Structure{},
									},									
									&Structure{
										Identifier: IdentifierString{"433"},
										Type: "part",
										Children: []*Structure{},
									},
								},
							},
						},
					},
				},
			},
			Part: "433",
			Depth: 3,
		},
		{
			Name: "test-not-found",
			Structure: Structure{
				Identifier: IdentifierString{"42"},
				Type: "title",
				Children: []*Structure{
					&Structure{
						Identifier: IdentifierString{"IV"},
						Type: "chapter",
						Children: []*Structure{
							&Structure{
								Identifier: IdentifierString{"C"},
								Type: "subchapter",
								Children: []*Structure{
									&Structure{
										Identifier: IdentifierString{"200"},
										Type: "part",
										Children: []*Structure{},
									},
								},
							},
						},
					},
				},
			},
			Part: "443",
			Depth: -1,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			depth := DeterminePartDepth(&tc.Structure, tc.Part)
			if depth != tc.Depth {
				t.Errorf("expected (%d), received (%d)", tc.Depth, depth)
			}
		})
	}
}

func TestDetermineParents(t *testing.T) {
	structure := Structure{
		Identifier: IdentifierString{"42"},
		Type: "title",
		Children: []*Structure{
			&Structure{
				Identifier: IdentifierString{"440"},
				Type: "part",
				Children: []*Structure{},
			},
			&Structure{
				Identifier: IdentifierString{"IV"},
				Type: "chapter",
				Children: []*Structure{
					&Structure{
						Identifier: IdentifierString{"C"},
						Type: "subchapter",
						Children: []*Structure{
							&Structure{
								Identifier: IdentifierString{"200"},
								Type: "part",
								Children: []*Structure{},
							},
							&Structure{
								Identifier: IdentifierString{"300"},
								Type: "part",
								Children: []*Structure{},
							},									
							&Structure{
								Identifier: IdentifierString{"433"},
								Type: "part",
								Children: []*Structure{},
							},
						},
					},
				},
			},
		},
	}

	expected := Structure{
		Identifier: IdentifierString{"42"},
		Type: "title",
		Parent: IdentifierString{},
		ParentType: "",
		Children: []*Structure{
			&Structure{
				Identifier: IdentifierString{"440"},
				Type: "part",
				Parent: IdentifierString{"42"},
				ParentType: "title",
				Children: []*Structure{},
			},
			&Structure{
				Identifier: IdentifierString{"IV"},
				Type: "chapter",
				Parent: IdentifierString{"42"},
				ParentType: "title",
				Children: []*Structure{
					&Structure{
						Identifier: IdentifierString{"C"},
						Type: "subchapter",
						Parent: IdentifierString{"IV"},
						ParentType: "chapter",
						Children: []*Structure{
							&Structure{
								Identifier: IdentifierString{"200"},
								Type: "part",
								Parent: IdentifierString{"C"},
								ParentType: "subchapter",
								Children: []*Structure{},
							},
							&Structure{
								Identifier: IdentifierString{"300"},
								Type: "part",
								Parent: IdentifierString{"C"},
								ParentType: "subchapter",
								Children: []*Structure{},
							},									
							&Structure{
								Identifier: IdentifierString{"433"},
								Type: "part",
								Parent: IdentifierString{"C"},
								ParentType: "subchapter",
								Children: []*Structure{},
							},
						},
					},
				},
			},
		},
	}

	DetermineParents(&structure)

	if diff := deep.Equal(structure, expected); diff != nil {
		t.Errorf("output not as expected: %+v", diff)
	}
}
