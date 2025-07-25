package errors

import "fmt"

var (
	ErrCacheMiss = fmt.Errorf("cache miss")
)
