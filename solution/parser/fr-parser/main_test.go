package main

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/cmsgov/cmcs-eregulations/lib/eregs"
	"github.com/cmsgov/cmcs-eregulations/lib/fedreg"

	log "github.com/sirupsen/logrus"
)

func TestLoadConfig(t *testing.T) {
	testTable := []struct {
		Name               string
		RetrieveConfigFunc func() (*eregs.ParserConfig, int, error)
		GetLogLevelFunc    func(string) log.Level
		Error              bool
	}{
		{
			Name: "test-load-config",
			RetrieveConfigFunc: func() (*eregs.ParserConfig, int, error) {
				return &eregs.ParserConfig{
					Workers:  1,
					Retries:  1,
					LogLevel: "warn",
					Parts: []*eregs.PartConfig{
						&eregs.PartConfig{
							Type:            "part",
							Title:           42,
							Value:           "400",
							UploadLocations: true,
							UploadRegText:   true,
							UploadFRDocs: true,
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
			RetrieveConfigFunc: func() (*eregs.ParserConfig, int, error) {
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

func TestStart(t *testing.T) {
	testTable := []struct {
		Name                  string
		LoadConfigFunc        func() (*eregs.ParserConfig, error)
		ProcessPartsListFunc  func(context.Context, int, []*eregs.PartConfig) ([]*eregs.PartConfig, error)
		ProcessPartFunc       func(context.Context, int, string, map[string]bool, bool, map[string]struct{}) error
		FetchDocumentListFunc func(context.Context) ([]string, error)
		Error                 bool
	}{
		{
			Name: "test-start",
			LoadConfigFunc: func() (*eregs.ParserConfig, error) {
				return &eregs.ParserConfig{
					Workers:  1,
					LogLevel: "warn",
					Parts: []*eregs.PartConfig{
						&eregs.PartConfig{
							Type:            "part",
							Title:           42,
							Value:           "400",
							UploadLocations: true,
							UploadRegText:   true,
							UploadFRDocs: true,
						},
					},
				}, nil
			},
			ProcessPartsListFunc: func(ctx context.Context, title int, parts []*eregs.PartConfig) ([]*eregs.PartConfig, error) {
				if title == 42 {
					return parts, nil
				} else {
					return nil, fmt.Errorf("bad title")
				}
			},
			ProcessPartFunc: func(ctx context.Context, title int, part string, existingDocs map[string]bool, skip bool, titles map[string]struct{}) error {
				return nil
			},
			FetchDocumentListFunc: func(ctx context.Context) ([]string, error) {
				return []string{"https://test.gov/test", "https://test.gov/test2"}, nil
			},
			Error: false,
		},
		{
			Name: "test-load-config-failure",
			LoadConfigFunc: func() (*eregs.ParserConfig, error) {
				return nil, fmt.Errorf("this is expected")
			},
			ProcessPartsListFunc: func(ctx context.Context, title int, parts []*eregs.PartConfig) ([]*eregs.PartConfig, error) {
				return []*eregs.PartConfig{}, nil
			},
			ProcessPartFunc: func(ctx context.Context, title int, part string, existingDocs map[string]bool, skip bool, titles map[string]struct{}) error {
				return nil
			},
			FetchDocumentListFunc: func(ctx context.Context) ([]string, error) {
				return []string{"https://test.gov/test", "https://test.gov/test2"}, nil
			},
			Error: true,
		},
		{
			Name: "test-process-part-failure",
			LoadConfigFunc: func() (*eregs.ParserConfig, error) {
				return &eregs.ParserConfig{
					Workers:  1,
					LogLevel: "warn",
					Parts: []*eregs.PartConfig{
						&eregs.PartConfig{
							Type:            "part",
							Title:           42,
							Value:           "400",
							UploadLocations: true,
							UploadRegText:   true,
							UploadFRDocs: true,
						},
					},
				}, nil
			},
			ProcessPartsListFunc: func(ctx context.Context, title int, parts []*eregs.PartConfig) ([]*eregs.PartConfig, error) {
				return parts, nil
			},
			ProcessPartFunc: func(ctx context.Context, title int, part string, existingDocs map[string]bool, skip bool, titles map[string]struct{}) error {
				return fmt.Errorf("this is expected")
			},
			FetchDocumentListFunc: func(ctx context.Context) ([]string, error) {
				return []string{"https://test.gov/test", "https://test.gov/test2"}, nil
			},
			Error: false,
		},
		{
			Name: "test-fetch-document-list-failure",
			LoadConfigFunc: func() (*eregs.ParserConfig, error) {
				return &eregs.ParserConfig{
					Workers:  1,
					LogLevel: "warn",
					Parts: []*eregs.PartConfig{
						&eregs.PartConfig{
							Type:            "part",
							Title:           42,
							Value:           "400",
							UploadLocations: true,
							UploadRegText:   true,
							UploadFRDocs: true,
						},
					},
				}, nil
			},
			ProcessPartsListFunc: func(ctx context.Context, title int, parts []*eregs.PartConfig) ([]*eregs.PartConfig, error) {
				return parts, nil
			},
			ProcessPartFunc: func(ctx context.Context, title int, part string, existingDocs map[string]bool, skip bool, titles map[string]struct{}) error {
				return fmt.Errorf("this is expected")
			},
			FetchDocumentListFunc: func(ctx context.Context) ([]string, error) {
				return nil, fmt.Errorf("this is expected")
			},
			Error: true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			loadConfigFunc = tc.LoadConfigFunc
			processPartsListFunc = tc.ProcessPartsListFunc
			processPartFunc = tc.ProcessPartFunc
			fetchDocumentListFunc = tc.FetchDocumentListFunc

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
		Name                string
		FetchContentFunc    func(context.Context, int, string) ([]*fedreg.FRDoc, error)
		ProcessDocumentFunc func(context.Context, int, string, *fedreg.FRDoc, map[string]struct{}) error
		ExistingDocs        map[string]bool
		SkipDocuments       bool
		Error               bool
	}{
		{
			Name: "test-process",
			FetchContentFunc: func(ctx context.Context, title int, part string) ([]*fedreg.FRDoc, error) {
				return []*fedreg.FRDoc{
					&fedreg.FRDoc{
						Name:        "a name",
						Description: "a description",
						Category:    "a doc type",
						URL:         "https://test.gov/test",
						Date:        "2021-01-31",
						DocketNumbers: []string{
							"CMS-0000-F2",
							"CMS-0001-C1",
						},
						DocumentNumber: "2021-12345",
					},
					&fedreg.FRDoc{
						Name:           "a name 2",
						Description:    "a description 2",
						Category:       "a doc type 2",
						URL:            "https://test.gov/test/2",
						Date:           "2021-02-01",
						DocketNumbers:  []string{"CMS-0000-F3"},
						DocumentNumber: "2021-67890",
					},
				}, nil
			},
			ProcessDocumentFunc: func(ctx context.Context, title int, part string, content *fedreg.FRDoc, titles map[string]struct{}) error {
				return nil
			},
			ExistingDocs:  map[string]bool{},
			SkipDocuments: false,
			Error:         false,
		},
		{
			Name: "test-fetch-fail",
			FetchContentFunc: func(ctx context.Context, title int, part string) ([]*fedreg.FRDoc, error) {
				return nil, fmt.Errorf("this is expected")
			},
			ProcessDocumentFunc: func(ctx context.Context, title int, part string, content *fedreg.FRDoc, titles map[string]struct{}) error {
				return nil
			},
			ExistingDocs:  map[string]bool{},
			SkipDocuments: false,
			Error:         true,
		},
		{
			Name: "test-process-fail",
			FetchContentFunc: func(ctx context.Context, title int, part string) ([]*fedreg.FRDoc, error) {
				return []*fedreg.FRDoc{
					&fedreg.FRDoc{
						Name:        "a name",
						Description: "a description",
						Category:    "a DocType",
						URL:         "https://test.gov/test",
						Date:        "2021-01-31",
						DocketNumbers: []string{
							"CMS-0000-F2",
							"CMS-0001-C1",
						},
						DocumentNumber: "2021-12345",
					},
					&fedreg.FRDoc{
						Name:           "a name 2",
						Description:    "a description 2",
						Category:       "a doc type 2",
						URL:            "https://test.gov/test/2",
						Date:           "2021-02-01",
						DocketNumbers:  []string{"CMS-0000-F3"},
						DocumentNumber: "2021-67890",
					},
				}, nil
			},
			ProcessDocumentFunc: func(ctx context.Context, title int, part string, content *fedreg.FRDoc, titles map[string]struct{}) error {
				return fmt.Errorf("this is expected")
			},
			ExistingDocs:  map[string]bool{},
			SkipDocuments: false,
			Error:         false,
		},
		{
			Name: "test-skip-documents",
			FetchContentFunc: func(ctx context.Context, title int, part string) ([]*fedreg.FRDoc, error) {
				return []*fedreg.FRDoc{
					&fedreg.FRDoc{
						Name:        "a name",
						Description: "a description",
						Category:    "a doc type",
						URL:         "https://test.gov/test",
						Date:        "2021-01-31",
						DocketNumbers: []string{
							"CMS-0000-F2",
							"CMS-0001-C1",
						},
						DocumentNumber: "2021-12345",
					},
					&fedreg.FRDoc{
						Name:           "a name 2",
						Description:    "a description 2",
						Category:       "a doc type 2",
						URL:            "https://test.gov/test/2",
						Date:           "2021-02-01",
						DocketNumbers:  []string{"CMS-0000-F3"},
						DocumentNumber: "2021-67890",
					},
				}, nil
			},
			ProcessDocumentFunc: func(ctx context.Context, title int, part string, content *fedreg.FRDoc, titles map[string]struct{}) error {
				return fmt.Errorf("this is expected")
			},
			ExistingDocs: map[string]bool{
				"https://test.gov/test": true,
			},
			SkipDocuments: true,
			Error:         false,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			fetchContentFunc = tc.FetchContentFunc
			processDocumentFunc = tc.ProcessDocumentFunc

			ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
			defer cancel()

			err := processPart(ctx, 42, "433", tc.ExistingDocs, tc.SkipDocuments, map[string]struct{}{"42": struct{}{}})
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
		Name              string
		FetchSectionsFunc func(context.Context, string, map[string]struct{}) ([]string, []string, map[string]string, error)
		SendDocumentFunc  func(context.Context, *eregs.FRDoc) error
		Error             bool
	}{
		{
			Name: "test-send",
			FetchSectionsFunc: func(ctx context.Context, path string, titles map[string]struct{}) ([]string, []string, map[string]string, error) {
				return []string{"433.12", "12.1", "1.1"}, nil, map[string]string{"433": "42", "12": "42", "1": "45"}, nil
			},
			SendDocumentFunc: func(ctx context.Context, doc *eregs.FRDoc) error {
				return nil
			},
			Error: false,
		},
		{
			Name: "test-fetch-sections-failure",
			FetchSectionsFunc: func(ctx context.Context, path string, titles map[string]struct{}) ([]string, []string, map[string]string, error) {
				return nil, nil, nil, fmt.Errorf("this is expected")
			},
			SendDocumentFunc: func(ctx context.Context, doc *eregs.FRDoc) error {
				if len(doc.Sections) != 0 {
					return fmt.Errorf("document locations length NOT zero")
				}
				return nil
			},
			Error: false,
		},
		{
			Name: "test-send-document-failure",
			FetchSectionsFunc: func(ctx context.Context, path string, titles map[string]struct{}) ([]string, []string, map[string]string, error) {
				return []string{"433.12", "12.1", "1.1"}, nil, map[string]string{"433": "42", "12": "42", "1": "45"}, nil
			},
			SendDocumentFunc: func(ctx context.Context, doc *eregs.FRDoc) error {
				return fmt.Errorf("this is expected")
			},
			Error: true,
		},
	}

	for _, tc := range testTable {
		t.Run(tc.Name, func(t *testing.T) {
			fetchSectionsFunc = tc.FetchSectionsFunc
			sendDocumentFunc = tc.SendDocumentFunc

			ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
			defer cancel()

			doc := fedreg.FRDoc{
				Name:        "a name",
				Description: "a description",
				Category:    "a doc type",
				URL:         "https://test.gov/test",
				Date:        "2021-01-31",
				DocketNumbers: []string{
					"CMS-0000-F2",
					"CMS-0001-C1",
				},
				DocumentNumber: "2021-12345",
				FullTextURL:    "http://test.gov/some/xml/url",
			}

			err := processDocument(ctx, 42, "433", &doc, map[string]struct{}{"42": struct{}{}})
			if err != nil && !tc.Error {
				t.Errorf("expected no error, received (%+v)", err)
			} else if err == nil && tc.Error {
				t.Errorf("expected error, received none")
			}
		})
	}
}
