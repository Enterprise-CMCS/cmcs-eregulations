module github.com/cmsgov/cmcs-eregulations/lib/parsexml

go 1.16

replace github.com/cmsgov/cmcs-eregulations/lib/ecfr => ../ecfr

replace github.com/cmsgov/cmcs-eregulations/lib/network => ../network

require (
	github.com/cmsgov/cmcs-eregulations/lib/ecfr v0.0.0-00010101000000-000000000000
	github.com/go-test/deep v1.0.8
	github.com/sirupsen/logrus v1.9.1
)
