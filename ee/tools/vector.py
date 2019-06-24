from osgeo import osr, ogr


class Vector():

    @staticmethod
    def Shape(geoJson):
        shape = ogr.GetDriverByName('MEMORY').CreateDataSource('')
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        layer = shape.CreateLayer("default", srs, ogr.wkbPolygon)
        feature = ogr.Feature(layer.GetLayerDefn())
        geometry = ogr.CreateGeometryFromJson(geoJson)
        feature.SetGeometry(geometry)
        layer.CreateFeature(feature)
        return shape

    @staticmethod
    def ReprojetLayer(layer, crs):
        sourceSR = layer.GetSpatialRef()
        targetSR = osr.SpatialReference()
        targetSR.ImportFromWkt(crs)

        coordTrans = osr.CoordinateTransformation(sourceSR, targetSR)
        feat = layer.GetNextFeature()
        geom = feat.GetGeometryRef()
        geom.Transform(coordTrans)
        return feat

    @staticmethod
    def Buffer(geoJson, distance, maxError, proj):
        geometry = ogr.CreateGeometryFromJson(geoJson)
        geometry_buffered = geometry.Buffer(distance)
        return geometry_buffered
