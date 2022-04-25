package main

import (
	"testing"
	"context"
	"time"
	"fmt"

	"github.com/cmsgov/cmcs-eregulations/fr-parser/eregs"
	"github.com/cmsgov/cmcs-eregulations/fr-parser/fedreg"
	ecfrEregs "github.com/cmsgov/cmcs-eregulations/ecfr-parser/eregs"
	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/ecfr"

	"github.com/go-test/deep"
	log "github.com/sirupsen/logrus"
)

func TestInit(t *testing.T) {
	if eregs.BaseURL != "http://localhost:8000/v3/" {
		t.Errorf("V3 URL not set correctly!")
	}
	if ecfrEregs.BaseURL != DefaultBaseURL {
		t.Errorf("V2 URL not set correctly!")
	}
}

func TestGetLogLevel(t *testing.T) {
	testTable := []struct {
		Name string
		Input string
		Expected log.Level
	}{
		{
			Name: "test-warn",
			Input: "warn",
			Expected: log.WarnLevel,
		},
		{
			Name: "test-fatal",
			Input: "fatal",
			Expected: log.FatalLevel,
		},
		{
			Name: "test-error",
			Input: "error",
			Expected: log.ErrorLevel,
		},
		{
			Name: "test-info",
			Input: "info",
			Expected: log.InfoLevel,
		},
		{
			Name: "test-debug",
			Input: "debug",
			Expected: log.DebugLevel,
		},
		{
			Name: "test-trace",
			Input: "trace",
			Expected: log.TraceLevel,
		},
		{
			Name: "test-default",
			Input: "not a valid level",
			Expected: log.WarnLevel,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func (t *testing.T) {
			out := getLogLevel(tc.Input)
			if out != tc.Expected {
				t.Errorf("expected (%+v), received (%+v)", tc.Expected, out)
			}
		})
	}
}

func TestLoadConfig(t *testing.T) {
	testTable := []struct {
		Name string
		RetrieveConfigFunc func () (*ecfrEregs.ParserConfig, int, error)
		GetLogLevelFunc func (string) log.Level
		Error bool
	}{
		{
			Name: "test-load-config",
			RetrieveConfigFunc: func() (*ecfrEregs.ParserConfig, int, error) {
				return &ecfrEregs.ParserConfig{
					Workers: 1,
					Attempts: 1,
					LogLevel: "warn",
					Titles: []*ecfrEregs.TitleConfig{
						&ecfrEregs.TitleConfig{
							Title: 42,
							Subchapters: ecfrEregs.SubchapterList{
								ecfrEregs.SubchapterArg{"IV", "C"},
								ecfrEregs.SubchapterArg{"IV", "D"},
							},
							Parts: ecfrEregs.PartList{"1", "2", "3"},
						},
					},
				}, 200, nil
			},
			GetLogLevelFunc: func(level string) log.Level {
				return log.WarnLevel
			},
			Error: false,
		},
		{
			Name: "test-load-config-failure",
			RetrieveConfigFunc: func() (*ecfrEregs.ParserConfig, int, error) {
				return nil, 400, fmt.Errorf("this is expected")
			},
			GetLogLevelFunc: func(level string) log.Level {
				return log.WarnLevel
			},
			Error: true,
		},
	}

	for _, tc := range testTable {
		retrieveConfigFunc = tc.RetrieveConfigFunc
		getLogLevelFunc = tc.GetLogLevelFunc
		config, err := loadConfig()
		if err != nil && !tc.Error {
			t.Errorf("expected no error, received (%+v)", err)
		} else if err == nil && tc.Error {
			t.Errorf("expected error, received (%+v)", config)
		}
	}
}

func TestGetPartsList(t *testing.T) {
	input := &ecfrEregs.TitleConfig{
		Title: 42,
		Subchapters: ecfrEregs.SubchapterList{
			ecfrEregs.SubchapterArg{"IV", "C"},
			ecfrEregs.SubchapterArg{"IV", "D"},
		},
		Parts: ecfrEregs.PartList{"1", "2", "3"},
	}

	extractSubchapterPartsFunc = func(ctx context.Context, date time.Time, title int, sub *ecfr.SubchapterOption) ([]string, error) {
		if sub.Chapter == "IV" && sub.Subchapter == "C" {
			return []string{"4", "5", "6"}, nil
		}
		return nil, fmt.Errorf("this is expected")
	}

	expected := []string{"4", "5", "6", "1", "2", "3"}

	ctx, cancel := context.WithTimeout(context.Background(), 1 * time.Second)
	defer cancel()

	output := getPartsList(ctx, input)

	if diff := deep.Equal(expected, output); diff != nil {
		t.Errorf("output not as expected: %+v", diff)
	}
}

func TestStart(t *testing.T) {
	testTable := []struct {
		Name string
		LoadConfigFunc func () (*ecfrEregs.ParserConfig, error)
		GetPartsListFunc func (context.Context, *ecfrEregs.TitleConfig) []string
		ProcessPartFunc func (context.Context, int, string) error
		Error bool
	}{
		{
			Name: "test-start",
			LoadConfigFunc: func() (*ecfrEregs.ParserConfig, error) {
				return &ecfrEregs.ParserConfig{
					Workers: 1,
					Attempts: 1,
					LogLevel: "warn",
					Titles: []*ecfrEregs.TitleConfig{
						&ecfrEregs.TitleConfig{
							Title: 42,
							Subchapters: ecfrEregs.SubchapterList{
								ecfrEregs.SubchapterArg{"IV", "C"},
								ecfrEregs.SubchapterArg{"IV", "D"},
							},
							Parts: ecfrEregs.PartList{"1", "2", "3"},
						},
						&ecfrEregs.TitleConfig{
							Title: 45,
							Subchapters: ecfrEregs.SubchapterList{
								ecfrEregs.SubchapterArg{"AB", "C"},
								ecfrEregs.SubchapterArg{"XY", "Z"},
							},
							Parts: ecfrEregs.PartList{"123", "456", "789"},
						},
					},
				}, nil
			},
			GetPartsListFunc: func(ctx context.Context, title *ecfrEregs.TitleConfig) []string {
				return []string{"1", "2", "3", "4", "5"}
			},
			ProcessPartFunc: func(ctx context.Context, title int, part string) error {
				return nil
			},
			Error: false,
		},
		{
			Name: "test-load-config-failure",
			LoadConfigFunc: func() (*ecfrEregs.ParserConfig, error) {
				return nil, fmt.Errorf("this is expected")
			},
			GetPartsListFunc: func(ctx context.Context, title *ecfrEregs.TitleConfig) []string {
				return []string{}
			},
			ProcessPartFunc: func(ctx context.Context, title int, part string) error {
				return nil
			},
			Error: true,
		},
		{
			Name: "test-process-part-failure",
			LoadConfigFunc: func() (*ecfrEregs.ParserConfig, error) {
				return &ecfrEregs.ParserConfig{
					Workers: 1,
					Attempts: 1,
					LogLevel: "warn",
					Titles: []*ecfrEregs.TitleConfig{
						&ecfrEregs.TitleConfig{
							Title: 42,
							Subchapters: ecfrEregs.SubchapterList{
								ecfrEregs.SubchapterArg{"IV", "C"},
								ecfrEregs.SubchapterArg{"IV", "D"},
							},
							Parts: ecfrEregs.PartList{"1", "2", "3"},
						},
						&ecfrEregs.TitleConfig{
							Title: 45,
							Subchapters: ecfrEregs.SubchapterList{
								ecfrEregs.SubchapterArg{"AB", "C"},
								ecfrEregs.SubchapterArg{"XY", "Z"},
							},
							Parts: ecfrEregs.PartList{"123", "456", "789"},
						},
					},
				}, nil
			},
			GetPartsListFunc: func(ctx context.Context, title *ecfrEregs.TitleConfig) []string {
				return []string{"1", "2", "3", "4", "5"}
			},
			ProcessPartFunc: func(ctx context.Context, title int, part string) error {
				return fmt.Errorf("this is expected")
			},
			Error: false,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func (t *testing.T) {
			loadConfigFunc = tc.LoadConfigFunc
			getPartsListFunc = tc.GetPartsListFunc
			processPartFunc = tc.ProcessPartFunc

			err := start()
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received none")
			}
		})
	}
}

func TestProcessPart(t *testing.T) {
	testTable := []struct {
		Name string
		FetchContentFunc func (context.Context, int, string) ([]*fedreg.FRDoc, error)
		ProcessDocumentFunc func (context.Context, int, string, *fedreg.FRDoc) error
		Error bool
	}{
		{
			Name: "test-process",
			FetchContentFunc: func(ctx context.Context, title int, part string) ([]*fedreg.FRDoc, error) {
				return []*fedreg.FRDoc{
					&fedreg.FRDoc{
						Name: "a name",
						Description: "a description",
						Category: "a category",
						URL: "https://test.gov/test",
						Date: "2021-01-31",
						DocketNumber: "CMS-0000-F2",
						DocumentNumber: "2021-12345",
					},
					&fedreg.FRDoc{
						Name: "a name 2",
						Description: "a description 2",
						Category: "a category 2",
						URL: "https://test.gov/test/2",
						Date: "2021-02-01",
						DocketNumber: "CMS-0000-F3",
						DocumentNumber: "2021-67890",
					},
				}, nil
			},
			ProcessDocumentFunc: func(ctx context.Context, title int, part string, content *fedreg.FRDoc) error {
				return nil
			},
			Error: false,
		},
		{
			Name: "test-fetch-fail",
			FetchContentFunc: func(ctx context.Context, title int, part string) ([]*fedreg.FRDoc, error) {
				return nil, fmt.Errorf("this is expected")
			},
			ProcessDocumentFunc: func(ctx context.Context, title int, part string, content *fedreg.FRDoc) error {
				return nil
			},
			Error: true,
		},
		{
			Name: "test-process-fail",
			FetchContentFunc: func(ctx context.Context, title int, part string) ([]*fedreg.FRDoc, error) {
				return []*fedreg.FRDoc{
					&fedreg.FRDoc{
						Name: "a name",
						Description: "a description",
						Category: "a category",
						URL: "https://test.gov/test",
						Date: "2021-01-31",
						DocketNumber: "CMS-0000-F2",
						DocumentNumber: "2021-12345",
					},
					&fedreg.FRDoc{
						Name: "a name 2",
						Description: "a description 2",
						Category: "a category 2",
						URL: "https://test.gov/test/2",
						Date: "2021-02-01",
						DocketNumber: "CMS-0000-F3",
						DocumentNumber: "2021-67890",
					},
				}, nil
			},
			ProcessDocumentFunc: func(ctx context.Context, title int, part string, content *fedreg.FRDoc) error {
				return fmt.Errorf("this is expected")
			},
			Error: false,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func (t *testing.T) {
			fetchContentFunc = tc.FetchContentFunc
			processDocumentFunc = tc.ProcessDocumentFunc

			ctx, cancel := context.WithTimeout(context.Background(), 1 * time.Second)
			defer cancel()

			err := processPart(ctx, 42, "433")
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received none")
			}
		})
	}
}

func TestProcessDocument(t *testing.T) {
	testTable := []struct {
		Name string
		FetchSectionsFunc func (context.Context, string, string) ([]string, error)
		SendDocumentFunc func (context.Context, *eregs.FRDoc) error
		Error bool
	}{
		{
			Name: "test-send",
			FetchSectionsFunc: func(ctx context.Context, date string, doc string) ([]string, error) {
				return []string{"433.12", "12.1", "1.1"}, nil
			},
			SendDocumentFunc: func(ctx context.Context, doc *eregs.FRDoc) error {
				return nil
			},
			Error: false,
		},
		{
			Name: "test-fetch-sections-failure",
			FetchSectionsFunc: func(ctx context.Context, date string, doc string) ([]string, error) {
				return nil, fmt.Errorf("this is expected")
			},
			SendDocumentFunc: func(ctx context.Context, doc *eregs.FRDoc) error {
				if len(doc.Locations) != 0 {
					return fmt.Errorf("document locations length NOT zero")
				}
				return nil
			},
			Error: false,
		},
		{
			Name: "test-send-document-failure",
			FetchSectionsFunc: func(ctx context.Context, date string, doc string) ([]string, error) {
				return []string{"433.12", "12.1", "1.1"}, nil
			},
			SendDocumentFunc: func(ctx context.Context, doc *eregs.FRDoc) error {
				return fmt.Errorf("this is expected")
			},
			Error: true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func (t *testing.T) {
			fetchSectionsFunc = tc.FetchSectionsFunc
			sendDocumentFunc = tc.SendDocumentFunc

			ctx, cancel := context.WithTimeout(context.Background(), 1 * time.Second)
			defer cancel()

			doc := fedreg.FRDoc{
				Name: "a name",
				Description: "a description",
				Category: "a category",
				URL: "https://test.gov/test",
				Date: "2021-01-31",
				DocketNumber: "CMS-0000-F2",
				DocumentNumber: "2021-12345",
			}

			err := processDocument(ctx, 42, "433", &doc)
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received none")
			}
		})
	}
}
