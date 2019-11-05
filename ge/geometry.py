#!/usr/bin/env python
import json

from osgeo import ogr, osr

import ge.apifunction
import ge.computedobject
import ge.ee_exception
import ge.ee_types
import ge.projection
import ge.serializer
from ge.tools.vector import Vector


class Geometry(ge.computedobject.ComputedObject):
    """
    https://pcjericks.github.io/py-gdalogr-cookbook/projection.html
    https://www.programcreek.com/python/example/58591/osgeo.osr.SpatialReference
    """

    def __init__(self, geo_json='', opt_proj='', opt_geodesic=None,
                 opt_evenOdd=None, **kwargs):
        """
        geo_json: "{ "type": "Polygon", "coordinates": [ [ 
            [ -5187287.790354605764151, -1906773.926006562076509 ], 
            [ -5187287.790354605764151, -1906773.926006562076509 ] ] ] }"
        opt_proj: "EPSG:4326" or ee.Projection()
        """
        super(Geometry, self).__init__(
            ge.apifunction.ApiFunction.lookup('Geometry.load'), kwargs)

        if geo_json:
            if not isinstance(geo_json, str):
                geo_json = json.dumps(geo_json)
            self._geometry = ogr.CreateGeometryFromJson(geo_json)

            if (opt_proj):
                if (not isinstance(opt_proj, ge.Projection)):
                    opt_proj = ge.Projection(opt_proj)

                targetSR = osr.SpatialReference()
                targetSR.ImportFromWkt(opt_proj.wkt())
                self._geometry.AssignSpatialReference(targetSR)

        else:
            self._geometry = None

    @staticmethod
    def Point(coords=[], proj=None):
        point = ogr.Geometry(ogr.wkbPoint)
        if len(coords) == 2:
            point.AddPoint_2D(coords[0], coords[1])
        elif len(coords) == 3:
            point.AddPoint(coords[0], coords[1], coords[2])

        geometry = Geometry(point.ExportToJson(), proj)
        return geometry

    @staticmethod
    def LineString(coords=[], proj=None):
        """
        :param coords: A list of at least two points. May be a list of coordinates in the GeoJSON 'LineString' format, a list of at least two ee.Geometry describing a point, or a list of at least four numbers defining the [x,y] coordinates of at least two points.
        :param proj: The projection of this geometry. If unspecified, the default is the projection of the input ee.Geometry, or EPSG:4326 if there are no ee.Geometry inputs.
        :return: Geometry
        """
        line = ogr.Geometry(ogr.wkbLineString)
        for coord in coords:
            if len(coord) == 2:
                line.AddPoint_2D(coord[0], coord[1])
            elif len(coord) == 3:
                line.AddPoint(coord[0], coord[1], coord[2])

        geometry = Geometry(line.ExportToJson(), proj)
        return geometry

    @staticmethod
    def LinearRing(coords=[], proj=None):
        """
        :param coords: A list of at least two points. May be a list of coordinates in the GeoJSON 'LineString' format, a list of at least two ee.Geometry describing 
            a point, or a list of at least four numbers defining the [x,y] coordinates of at least two points.
        :param proj: The projection of this geometry. If unspecified, the default is the projection of the input ee.Geometry, or EPSG:4326 if there are no 
            ee.Geometry inputs.
        :return: Geometry
        """
        ring = ogr.Geometry(ogr.wkbLinearRing)
        first = coords[0]
        last = coords[-1]
        if first != last:
            coords.append(first)
        for coord in coords:
            if len(coord) == 2:
                ring.AddPoint_2D(coord[0], coord[1])
            elif len(coord) == 3:
                ring.AddPoint(coord[0], coord[1], coord[2])

        if (proj):
            geometry = Geometry(ring.ExportToJson(), proj)
        else:
            geometry = Geometry()
            geometry._geometry = ring
        return geometry

    @staticmethod
    def Polygon(coords=[], proj=None):
        ring = Geometry.LinearRing(coords)

        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring._geometry)

        if (proj):
            geometry = Geometry(poly.ExportToJson(), proj)
        else:
            geometry = Geometry()
            geometry._geometry = poly
        return geometry

    @staticmethod
    def MultiLineString(coords=[], proj=None):
        multilinestring = ogr.Geometry(ogr.wkbMultiLineString)
        for coord in coords:
            line = Geometry.LineString(coord)
            multilinestring.AddGeometry(line._geometry)

        if (proj):
            geometry = Geometry(multilinestring.ExportToJson(), proj)
        else:
            geometry = Geometry()
            geometry._geometry = multilinestring
        return geometry

    @staticmethod
    def MultiPoint(coords=[], proj=None):
        multipoint = ogr.Geometry(ogr.wkbMultiPoint)
        for coord in coords:
            point = Geometry.Point(coord)
            multipoint.AddGeometry(point._geometry)

        if (proj):
            geometry = Geometry(multipoint.ExportToJson(), proj)
        else:
            geometry = Geometry()
            geometry._geometry = multipoint
        return geometry

    @staticmethod
    def MultiPolygon(coords=[], proj=None):
        multipolygon = ogr.Geometry(ogr.wkbMultiPolygon)
        for coord in coords:
            polygon = Geometry.Polygon(coord)
            multipolygon.AddGeometry(polygon._geometry)

        if (proj):
            geometry = Geometry(multipolygon.ExportToJson(), proj)
        else:
            geometry = Geometry()
            geometry._geometry = multipolygon
        return geometry

    @staticmethod
    def Rectangle(coords=[], proj=None):
        pass

    def buffer(self, distance, proj=None, maxError=None):
        """
        Returns the input buffered by a given distance. If the distance is positive,
        the geometry is expanded, and if the distance is negative, the geometry is contracted.
        :param distance: The distance of the buffering, which may be negative. If no projection
        is specified, the unit is meters. Otherwise the unit is in the coordinate system of the projection.
        :param maxError: The maximum amount of error tolerated when approximating the buffering
        circle and performing any necessary reprojection. If unspecified, defaults to 1% of the distance.
        :param proj: If specified, the buffering will be performed in this projection and the
        distance will be interpreted as units of the coordinate system of this projection.
        Otherwise the distance is interpereted as meters and the buffering is performed in a
        spherical coordinate system.
        """
        geometry = self.copy()
        if not proj:
            proj = self.projection()

        geometry = geometry.transform(proj)
        geometry_buffered = geometry._geometry.Buffer(distance)
        geometry = Geometry(geometry_buffered.ExportToJson(), proj)

        return geometry

    def transform(self, proj=None, maxError=None):
        """
        Transforms the geometry to a specific projection.
        :param proj: The target projection. Defaults to WGS84. If this has a geographic CRS,
        the edges of the geometry will be interpreted as geodesics. Otherwise they will be
        interpreted as straight lines in the projection (e.g. 'EPSG:4326') or a WKT string
        
        :param maxError: The maximum projection error.
        """

        if (not isinstance(proj, ge.Projection)):
            proj = ge.Projection(proj)

        geometry = self.copy()

        source = osr.SpatialReference()
        source.ImportFromWkt(geometry.projection().wkt())

        target = osr.SpatialReference()
        target.ImportFromWkt(proj.wkt())

        trans = osr.CoordinateTransformation(source, target)

        geometry._geometry.Transform(trans)

        return geometry

    def projection(self):
        """
        Returns the projection of the geometry.
        """
        if self._geometry.GetSpatialReference():
            return ge.Projection(
                self._geometry.GetSpatialReference().ExportToWkt())
        return None

    def area(self, maxError=None, proj=None):
        return self._geometry.GetArea()

    def length(self, maxError=None, proj=None):
        return self._geometry.Length()

    def type(self):
        return self._geometry.GetGeometryName()

    def intersection(self, right, maxError=None, proj=None):
        return self.applyFunc(ogr.Geometry.Intersection, right)

    def intersects(self, right, maxError=None, proj=None):
        return self._geometry.Intersects(right._geometry)

    def union(self, right, maxError=None, proj=None):
        return self.applyFunc(ogr.Geometry.Union, right)

    def difference(self, right, maxError=None, proj=None):
        return self.applyFunc(ogr.Geometry.Difference, right)

    def contains(self, right, maxError=None, proj=None):
        return self.applyAtomicFunc(ogr.Geometry.Contains, right)

    def convexHull(self, maxError=None, proj=None):
        return self.applyFunc(ogr.Geometry.ConvexHull)

    def coordinates(self):
        geometry = self.getInfo()
        return geometry["coordinates"]

    def centroid(self):
        geometry = self.copy()
        geometry._geometry = geometry._geometry.Centroid()
        return geometry

    def bounds(self):
        geometry = self.copy()
        shape = Vector.Shape(geometry.toGeoJSON())
        bounds = shape.GetLayer().GetExtent()
        return bounds

    def applyAtomicFunc(self, func, other=None):
        if other:
            return func(self._geometry, other._geometry)
        else:
            return func(self._geometry)

    def getInfo(self):
        geometry = json.loads(self._geometry.ExportToJson())
        return geometry

    def applyFunc(self, func, other=None):
        geometry = self.copy()
        geometry._geometry = self.applyAtomicFunc(func, other)
        return geometry

    def toGeoJSON(self):
        return self._geometry.ExportToJson()

    def toGeoJSONString(self):
        return json.dumps(self.toGeoJSON())

    def encode(self, opt_encoder=None):
        if self._geometry is not None:
            return opt_encoder(self._geometry)
        else:
            return super(Geometry, self).encode(opt_encoder)

    def copy(self):
        return Geometry(self.toGeoJSON(), self.projection())

    @staticmethod
    def name():
        return 'Geometry'
