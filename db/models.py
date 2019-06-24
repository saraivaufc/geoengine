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
    path = StringField()
    imageCollection = ReferenceField(ImageCollection, reverse_delete_rule=2)
    file = FileField(required=True)
    properties = DictField()

    meta = {
        'collection': 'images'
    }

class FeatureCollection(DynamicDocument):
    type = StringField(default="FeatureCollection")
    properties = DictField()

    meta = {
        'collection': 'featureCollections'
    }


class Feature(DynamicDocument):
    type = StringField(default="Feature")
    featureCollection = LazyReferenceField(document_type=FeatureCollection,
                                           reverse_delete_rule=True,
                                           passthrough=True)
    geometry = DynamicField()
    properties = DictField()

    meta = {
        'collection': 'features'
    }
