# GUS - Gitlab Update Service

Fork- and Update-Service for ADEQUATe Gitlab projects.

## Install
1. (optional) create a virtual environment
* `$ virtualenv --system-site-packages gus`
* `$ . gus/bin/activate`
2. install the service via pip 
* `$ (gus) pip install git+git://github.com/ADEQUATeDQ/GUS.git`
3. run the service
* `$ (gus) gus --help`
* `$ (gus) gus --gitlab http://data.adequate.at/ --port 5000`
* > Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
