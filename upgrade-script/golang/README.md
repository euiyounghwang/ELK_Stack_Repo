<i> 

## Golang Setup

GoNB offers a pre-built docker, that includes JupyterLab and GoNB. To use it, go to a directory that you want to make available to the Jupyter notebook (your home directory, or a directory where to store the notebook files). It will be mounted on the host/ subdirectory in JupyterLab.

https://pkg.go.dev/github.com/janpfeifer/gonb#section-readme

Window (Docker based)
- docker pull janpfeifer/gonb_jupyterlab:latest
- docker run -it --rm -p 8888:8888 -v "${PWD}":/notebooks janpfeifer/gonb_jupyterlab:latest
- docker cp loving_greider:/notebooks .

Linux and macOS Installation Using Standard Go Tools
- go install github.com/janpfeifer/gonb@latest && \
  go install golang.org/x/tools/cmd/goimports@latest && \
  go install golang.org/x/tools/gopls@latest

- goplay : go install -v github.com/haya14busa/goplay/cmd/goplay@v1.0.0

## Golang
If you’re starting a new project, create a new module by running the following command: (https://opensearch.org/docs/latest/clients/go/)
- go mod init <mymodulename>
- go mod tidy
- go run main.go
- go build
- compile a go file/project on windows for Linux: `env GOOS=linux go build -o ./bin/prometheus` (Run this command `chmod 755 filname` after copying to linux server)
