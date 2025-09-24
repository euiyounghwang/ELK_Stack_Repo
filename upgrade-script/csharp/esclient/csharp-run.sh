#!/bin/bash
set -e


SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

echo "C# Run"

# --
# dotnet new console esclient
# dotnet add package NEST --version 7.17.4
# dotnet add package DotNetEnv

# --
# In some cases, especially after creating a new project or making significant changes, running dotnet build before dotnet run can help ensure all dependencies are resolved and the project is in a runnable state.
# dotnet build
# dotnet run

dotnet run --project ./esclient.csproj
# dotnet run ./esclient/ES_Client.cs



