# Open Data Graph
## Dependencies
* YAJL
```shell script
sudo apt-get install libyajl-dev
```
* Python 3.6
* Install pip requirements
```shell script
pip install -r requirements.txt
```

## Run with gurnicorn
```shell script
gunicorn -b 127.0.0.1:5000 "app:create_app()"
```
