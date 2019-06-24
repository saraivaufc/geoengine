# earth-engine

# Earh Engine

### Requirements
* GDAL -- [Homepage](http://www.gdal.org)
* TensorFlow -- [Homepage](https://www.tensorflow.org)


### Install Gdal
Get gdal development libraries:
```shell
$ sudo apt-add-repository ppa:ubuntugis/ubuntugis-unstable
$ sudo apt-get update
$ sudo apt-get install libgdal-dev
$ sudo apt-get install python3-dev
$ sudo apt-get install gdal-bin python3-gdal
```


### Install and initialize redis
```shell
$ sudo apt-get install redis-server
$ sudo systemctl enable redis-server.service
$ sudo service redis-server start
```

### Install MongoDB
```shell
$ sudo apt install -y mongodb
```
### Create and activate a virtual environment
```shell
$ virtualenv env -p python3
$ source env/bin/activate
```

### Install Numpy
```shell
(env) $ pip3 install numpy
```
### Install GDAL
```shell
(env) $ pip3 install GDAL==$(gdal-config --version) --global-option=build_ext --global-option="-I/usr/include/gdal"
```

### Install Tensorflow with GPU
```shell
```shell
(env) $ pip3 install tensorflow-gpu==2.0.0b1
```

### Install MongoEngine
```shell
```shell
(env) $ pip3 install mongoengine
```

Install Others Requirements
```shell
(env) $ pip3 install -r requirements.txt
```
```