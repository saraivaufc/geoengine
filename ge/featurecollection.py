import json
from urllib.parse import urlparse

from osgeo import ogr

import ge.apifunction
import ge.element
from ge.collection import Collection
from ge.db import models
from ge.ee_list import List
from ge.geometry import Geometry


class FeatureCollection(Collection):
    def __init__(self, *args, **kwargs):
        super(FeatureCollection, self).__init__(
            ge.apifunction.ApiFunction.lookup('Vector.load'), kwargs)

        self._id = ""
        self._columns = List([])
        self._fields = List([])
        self._features = List([])
        self.__dict__.update(kwargs)

        if len(args) > 0:
            if isinstance(args[0], str):
                vector = self.load(args[0])
                self._features = vector._features or List([])
                self._properties = vector._properties or List([])

    def features(self):
        return self._features

    @staticmethod
    def load(id):
        id = urlparse(id)

        if id.scheme == "db":
            vector = FeatureCollection._loadFromDatabase(id.netloc + id.path)
        else:
            vector = FeatureCollection._loadFromLocalDisk(id.path)
        return vector

    @staticmethod
    def _loadFromLocalDisk(id):
        vector = FeatureCollection()
        vector._id = id

        dataSource = ogr.Open(id)
        layer = dataSource.GetLayer()
        layerDefinition = layer.GetLayerDefn()

        # load field
        for i in range(layerDefinition.GetFieldCount()):
            fieldName = layerDefinition.GetFieldDefn(i).GetName()
            fieldTypeCode = layerDefinition.GetFieldDefn(i).GetType()
            fieldType = layerDefinition.GetFieldDefn(i).GetFieldTypeName(
                fieldTypeCode)
            fieldWidth = layerDefinition.GetFieldDefn(i).GetWidth()
            fieldPrecision = layerDefinition.GetFieldDefn(i).GetPrecision()

            field = Column(fieldName, fieldType, fieldWidth, fieldPrecision)
            vector._fields = vector._fields.add(field)

        # load features
        for feature in layer:
            feature_json = json.loads(feature.ExportToJson())

            feature_type = feature.GetGeometryRef().GetGeometryName()
            feature_geometry = Geometry(
                geo_json=feature.GetGeometryRef().ExportToJson(),
                opt_proj=feature.GetGeometryRef().GetSpatialReference().ExportToWkt()
            )
            feature_properties = feature_json.get("properties")

            feature = Feature(type=feature_type, geometry=feature_geometry)

            for key, value in feature_properties.items():
                feature = feature.set(key, value)

            vector._features = vector._features.add(feature)

        return vector

    @staticmethod
    def _loadFromDatabase(dataSourceNamePrefix):
        vector = FeatureCollection()
        code = dataSourceNamePrefix.replace("db://", "")
        vector._id = code
        vector._features = ge.List([])

        featureCollection = models.FeatureCollection \
            .objects(code=code) \
            .first()

        features = models.Feature.objects(featureCollection=featureCollection)
        for f in features:
            feature_geometry = Geometry(
                geo_json=f.geometry
            )

            feature = Feature(type=f.type,
                              geometry=feature_geometry)

            for key, value in f.properties.items():
                feature = feature.set(key, value)

            vector._features.add(feature)

        return vector

    def filterBounds(self, geometry):
        vector = FeatureCollection()
        features = ge.List([])
        for feature in self._features:
            intersects = geometry.intersects(feature.geometry())
            if intersects:
                features.add(feature)

        vector._features = features
        return vector

    def compute(self):
        return self

    def copy(self):
        return FeatureCollection(self.args, **self.__dict__)

    def size(self):
        return self._features.length()

    def first(self):
        return self._features.get(0)

    def toList(self, count, offset=0):
        return self.features().slice(offset, offset + count)

    @staticmethod
    def name():
        return 'Vector'

    @staticmethod
    def elementType():
        return Feature


class Column(ge.element.Element):
    def __init__(self, name, type, width, precision, **kwargs):
        super(Column, self).__init__(
            ge.apifunction.ApiFunction.lookup('FeatureCollection.column'),
            kwargs)
        self._name = name
        self._type = type
        self._width = width
        self._precision = precision

        self.__dict__.update(kwargs)

    def getName(self):
        return self._name

    def getType(self):
        return self._type

    def getWidth(self):
        return self._width

    def getPrecision(self):
        return self._precision

    def setType(self, type):
        feature = self.copy()
        feature._type = type
        return feature

    def copy(self):
        return Column(self._name, self._type, self._width, self._precision,
                      **self.__dict__)

    @staticmethod
    def name():
        return 'Column'


class Feature(ge.element.Element):
    def __init__(self, type, geometry, **kwargs):
        super(Feature, self).__init__(
            ge.apifunction.ApiFunction.lookup('FeatureCollection.feature'),
            kwargs)
        self._type = type
        self._geometry = geometry
        self.__dict__.update(kwargs)

    def type(self):
        return self._type

    def geometry(self):
        return self._geometry

    def copy(self):
        return Feature(self._type, self._geometry, **self.__dict__)

    @staticmethod
    def name():
        return 'Feature'
