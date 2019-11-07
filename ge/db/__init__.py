import os

from mongoengine import connect

DB_NAME = os.environ.get("ENGINE_DB_NAME", "engine")
DB_HOST = os.environ.get("ENGINE_DB_HOST", "localhost")

connect(host='mongodb://{DB_HOST}/{DB_NAME}'.format(
    DB_HOST=DB_HOST,
    DB_NAME=DB_NAME
))