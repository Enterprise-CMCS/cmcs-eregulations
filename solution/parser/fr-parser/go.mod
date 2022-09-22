module github.com/cmsgov/cmcs-eregulations/fr-parser

go 1.16

require (
	github.com/aws/aws-lambda-go v1.30.0
	github.com/cmsgov/cmcs-eregulations/ecfr-parser v0.0.0-00010101000000-000000000000
	github.com/cmsgov/cmcs-eregulations/network v0.0.0-00010101000000-000000000000
	github.com/go-test/deep v1.0.8
	github.com/sirupsen/logrus v1.9.0
)

replace github.com/cmsgov/cmcs-eregulations/ecfr-parser => ../ecfr-parser

replace github.com/cmsgov/cmcs-eregulations/network => ../network
