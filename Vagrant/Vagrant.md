
#### Vagrnt Install
- vagrant up --provider=docker
- vagrant ssh
- vagrant ssh -- -L 9901:localhost:9201 -L 9000:localhost:9200 -L 5602:localhost:5601 -L 5603:localhost:5602 -L 5672:localhost:5672 -L 15672:localhost:15672 -L 5432:localhost:5432 -L 8080:localhost:8080 -L 8081:localhost:8081


#### Vagrnt SSH OS Install
```bash

sudo apt-get install wget vim python3-venv net-tools


wget --output-file ./miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-4.7.12.1-Linux-x86_64.sh
chmod +rx *.sh
```