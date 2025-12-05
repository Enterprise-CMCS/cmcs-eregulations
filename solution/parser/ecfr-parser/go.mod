module github.com/cmsgov/cmcs-eregulations/ecfr-parser

go 1.16

require (
	github.com/aws/aws-lambda-go v1.27.1
	github.com/cmsgov/cmcs-eregulations/lib/ecfr v0.0.0-00010101000000-000000000000
	github.com/cmsgov/cmcs-eregulations/lib/eregs v0.0.0-00010101000000-000000000000
	github.com/cmsgov/cmcs-eregulations/lib/parsexml v0.0.0-00010101000000-000000000000
	github.com/go-test/deep v1.0.8
	github.com/sirupsen/logrus v1.9.1
)

replace github.com/cmsgov/cmcs-eregulations/lib/network => ../lib/network

replace github.com/cmsgov/cmcs-eregulations/lib/parsexml => ../lib/parsexml

replace github.com/cmsgov/cmcs-eregulations/lib/eregs => ../lib/eregs

replace github.com/cmsgov/cmcs-eregulations/lib/ecfr => ../lib/ecfr
