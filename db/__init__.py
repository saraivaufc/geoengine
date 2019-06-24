from mongoengine import connect
from conf import settings


DATABASE = getattr(settings, "DATABASE", "default")

connect(DATABASE)