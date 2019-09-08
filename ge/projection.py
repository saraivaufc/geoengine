import re

from osgeo import osr


class Projection(object):
    def __init__(self, crs, transform=None, transformWkt=None):
        """
        Returns a Projection with the given base coordinate system and the
        given transform between projected coordinates and the base. If no
        transform is specified, the identity transform is assumed.

        :param crs: The base coordinate reference system of this Projection,
        given as a well-known authority code (e.g. 'EPSG:4326') or a WKT
        string.

        :param transform: The transform between projected coordinates and the
        base coordinate system, specified as a 2x3 affine transform matrix in
        row-major order: [xScale, xShearing, xTranslation, yShearing, yScale,
        yTranslation]. May not specify both this and 'transformWkt'.

        :param transformWkt: The transform between projected coordinates and
        the base coordinate system, specified as a WKT string. May not specify
        both this and 'transform'.
        """
        if (crs):
            self._crs = osr.SpatialReference()
            search = re.search('EPSG:(\w+)', crs)
            if (search and len(search.groups()) >= 1):
                epsg_code = int(search.groups()[0])
                self._crs.ImportFromEPSG(epsg_code)
            else:
                self._crs.ImportFromWkt(crs)

            self._transformWkt = self._crs.ExportToWkt()
        else:
            self._transform = transform
            self._transformWkt = transformWkt

    def atScale(self, meters):
        """
        Returns the projection scaled such that its units have the given scale
        in linear meters, as measured at the point of true scale.
        :param meters:
        """
        pass

    def crs(self):
        """
        Returns the authority code (e.g. 'EPSG:4326') for the base coordinate
        system of this projection, or null if the base coordinate system is not
        found in any available database
        """
        if (self._crs):
            return self._crs.ExportToWkt()
        else:
            return None

    def nominalScale(self):
        """
        Returns the linear scale in meters of the units of this projection, as
        measured at the point of true scale.
        """
        pass

    def scale(self, x, y):
        """
        Returns the projection scaled by the given amount in each axis.
        :param x:
        :param y:
        """
        pass

    def transform(self):
        """
        Returns a WKT representation of the transform of this Projection.
        This is the transform that converts from projected coordinates to the
        base coordinate system.
        """
        return self._transform

    def wkt(self):
        """
        Returns a WKT representation of the base coordinate system of this
        Projection.
        """
        return self._transformWkt
