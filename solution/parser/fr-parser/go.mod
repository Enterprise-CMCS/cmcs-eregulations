module github.com/cmsgov/cmcs-eregulations/fr-parser

go 1.16

require (
	github.com/aws/aws-lambda-go v1.30.0
	github.com/cmsgov/cmcs-eregulations/lib/eregs v0.0.0-00010101000000-000000000000
	github.com/cmsgov/cmcs-eregulations/lib/fedreg v0.0.0-00010101000000-000000000000
	github.com/sirupsen/logrus v1.9.1
)

replace github.com/cmsgov/cmcs-eregulations/lib/fedreg => ../lib/fedreg

replace github.com/cmsgov/cmcs-eregulations/lib/ecfr => ../lib/ecfr

replace github.com/cmsgov/cmcs-eregulations/lib/eregs => ../lib/eregs

replace github.com/cmsgov/cmcs-eregulations/lib/network => ../lib/network

replace github.com/cmsgov/cmcs-eregulations/lib/parsexml => ../lib/parsexml
