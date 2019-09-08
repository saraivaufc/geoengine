from mongoengine import connect
from ge import settings

DATABASE = getattr(settings, "DATABASE", "default")

connect(DATABASE)