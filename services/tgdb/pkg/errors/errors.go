package errors

import (
	"errors"
	"fmt"
	"google.golang.org/grpc/codes"
	"net/http"
)

const (
	msgCacheMiss = "cache miss"
	msgNotFound  = "not found"
	msgConflict  = "conflict"
	msgInternal  = "internal error"
)

var (
	ErrCacheMiss = fmt.Errorf(msgCacheMiss)
	ErrNotFound  = fmt.Errorf(msgNotFound)
	ErrConflict  = fmt.Errorf(msgConflict)
)

type Error struct {
	err error
}

func New(err error) *Error {
	return &Error{err: err}
}

func (e *Error) Error() string {
	return e.err.Error()
}

func (e *Error) PublicMessage() string {
	if errors.Is(e.err, ErrNotFound) {
		return msgNotFound
	}

	if errors.Is(e.err, ErrConflict) {
		return msgConflict
	}

	return msgInternal
}

func (e *Error) GRPCCode() codes.Code {
	return resolveGRPCCode(e.err)
}

func (e *Error) HttpCode() int {
	return resolveHttpCode(e.err)
}

func resolveGRPCCode(err error) codes.Code {
	if errors.Is(err, ErrNotFound) {
		return codes.NotFound
	}

	if errors.Is(err, ErrConflict) {
		return codes.AlreadyExists
	}

	return codes.Internal
}

func resolveHttpCode(err error) int {
	if errors.Is(err, ErrNotFound) {
		return http.StatusNotFound
	}

	if errors.Is(err, ErrConflict) {
		return http.StatusConflict
	}

	return http.StatusInternalServerError
}
