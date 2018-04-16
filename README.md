# GUS - Gitlab Update Service

Fork- and Update-Service for ADEQUATe Gitlab projects.

## Install
1. (optional) create a virtual environment
* `$ virtualenv --system-site-packages gus`
* `$ . gus/bin/activate`
2. install the service via pip 
* `$ (gus) pip install git+git://github.com/ADEQUATeDQ/GUS.git`
## Run 
* `$ (gus) gus --help`
* `$ (gus) gus --gitlab http://data.adequate.at/ --port 5000`
* > Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
## Docker
The service is also via [Docker available](https://hub.docker.com/r/sebneu/gus/)
* `$ docker pull sebneu/gus`
* `$ docker run --rm sebneu/gus --help`
* `$ docker run -d -p 5000:5000 --name gus sebneu/gus`
