from mongoengine import connect
from ge import settings

DATABASE = getattr(settings, "DATABASE", "earth_engine")

connect(DATABASE)