module github.com/cmsgov/cmcs-eregulations/fr-parser

go 1.16

require (
	github.com/aws/aws-lambda-go v1.30.0 // indirect
	github.com/cmsgov/cmcs-eregulations/ecfr-parser v0.0.0-00010101000000-000000000000 // indirect
	github.com/sirupsen/logrus v1.8.1 // indirect
)

replace github.com/cmsgov/cmcs-eregulations/ecfr-parser => ../ecfr-parser
