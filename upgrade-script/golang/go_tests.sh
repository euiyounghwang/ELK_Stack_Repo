#!/bin/bash

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# go get github.com/joho/godotenv
# github.com/stretchr/testify/assert

# go test -v ./tests/test_api_test.go

go test -v ./tests/