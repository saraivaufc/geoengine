from mongoengine import *


class ImageCollection(DynamicDocument):
    # LANDSAT/LC08/C01/T1_TOA
    path = StringField()
    descrition = StringField()
    properties = DictField()
    meta = {
        'collection': 'imageCollections'
    }

class Image(DynamicDocument):
    path = StringField(required=True)
    imageCollection = LazyReferenceField(ImageCollection,
                                         reverse_delete_rule=2)
    file = FileField(required=True)
    properties = DictField()

    meta = {
        'collection': 'images'
    }

class FeatureCollection(DynamicDocument):
    path = StringField()
    type = StringField(default="FeatureCollection")
    properties = DictField()

    meta = {
        'collection': 'featureCollections'
    }


class Feature(DynamicDocument):
    type = StringField(default="Feature")
    featureCollection = LazyReferenceField(FeatureCollection,
                                           reverse_delete_rule=2)
    geometry = DynamicField()
    properties = DictField()

    meta = {
        'collection': 'features'
    }
