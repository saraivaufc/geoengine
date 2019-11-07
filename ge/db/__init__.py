import os

from mongoengine import connect

DB_NAME = os.environ.get("GEOENGINE_DB_NAME", "earth_engine")
DB_HOST = os.environ.get("GEOENGINE_DB_HOST", "localhost")

connect(host='mongodb://{DB_HOST}/{DB_NAME}'.format(
    DB_HOST=DB_HOST,
    DB_NAME=DB_NAME
))