package main

import (
	"io"
)

func writeData(f io.Writer, data []byte) error {
	_, err := f.Write(data)
	return err
}
