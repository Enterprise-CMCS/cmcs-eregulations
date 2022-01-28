package main

import (
	"testing"

	"github.com/cmsgov/cmcs-eregulations/ecfr-parser/eregs"
)

func TestInit(t *testing.T) {
	if eregs.BaseURL != DefaultBaseURL {
		t.Errorf("eregs.BaseURL: expected (%s), received (%s)", DefaultBaseURL, eregs.BaseURL)
	}
}

//NOT IMPLEMENTED
func TestParseConfig(t *testing.T) {
	
}

//NOT IMPLEMENTED
//SHOULD NOT TEST IF POSSIBLE
func TestLambdaHandler(t *testing.T) {
	
}

//NOT IMPLEMENTED
//SHOULD NOT TEST IF POSSIBLE
func TestMainFunction(t *testing.T) {
	
}

//NOT IMPLEMENTED
func TestStart(t *testing.T) {
	
}

//NOT IMPLEMENTED
func TestParseTitle(t *testing.T) {
	
}

//NOT IMPLEMENTED
func TestStartHandlePartVersionWorker(t *testing.T) {
	
}

//NOT IMPLEMENTED
func TestHandlePartVersion(t *testing.T) {
	
}

//NOT IMPLEMENTED
func TestContains(t *testing.T) {
	
}
