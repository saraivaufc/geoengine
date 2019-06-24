import numpy
from osgeo import gdal, osr

from .vector import Vector


class Raster(object):
    @staticmethod
    def ClipByGeometry(dataset, geo_json, all_touched=False):
        shape = Vector.Shape(geo_json)
        layer = shape.GetLayer()

        feat = Vector.ReprojetLayer(layer, dataset.GetProjectionRef())

        pointsX, pointsY = Raster.get_extent_of_feat(feat)

        x_origin, pixel_width, _, y_origin, _, pixel_height = dataset.GetGeoTransform()

        xmin, xmax, ymin, ymax = Raster.get_extent_coords(pointsX, pointsY)
        xoff, yoff, xcount, ycount = Raster.specify_offset_of_rows_and_columns(xmin, xmax, ymin, ymax, x_origin,
                                                                               y_origin, pixel_width)

        mem_dataset = gdal.GetDriverByName('MEM').Create('', xcount, ycount, dataset.RasterCount,
                                                         dataset.GetRasterBand(1).DataType)
        mem_dataset.SetProjection(dataset.GetProjectionRef())
        mem_dataset.SetGeoTransform((xmin, pixel_width, 0, ymax, 0, pixel_height))

        gdal.RasterizeLayer(mem_dataset, [1], layer, burn_values=[1], options=["ALL_TOUCHED={}".format(all_touched)])

        for i in range(1, mem_dataset.RasterCount + 1):
            dataset_array = dataset.GetRasterBand(i).ReadAsArray().astype(numpy.float)[yoff:yoff + ycount,
                            xoff:xoff + xcount]
            dataset_mask = dataset.GetRasterBand(i).ReadAsArray().astype(numpy.float)[0:dataset_array.shape[0],
                           0:dataset_array.shape[1]]

            zoneraster = numpy.ma.masked_array(dataset_array, numpy.logical_not(dataset_mask))
            zoneraster.set_fill_value(numpy.nan)

            mem_dataset.GetRasterBand(i).WriteArray(zoneraster)

        return mem_dataset

    @staticmethod
    def Reproject(dataset, crs, crsTransform=None, scale=None):

        crs_from = osr.SpatialReference(wkt=dataset.GetProjectionRef())
        crs_to = osr.SpatialReference(wkt=crs)

        tx = osr.CoordinateTransformation(crs_from, crs_to)

        x_size = dataset.RasterXSize
        y_size = dataset.RasterYSize

        transform = dataset.GetGeoTransform()
        if not crsTransform:
            crsTransform = transform

        # Work out the boundaries of the new dataset in the target projection
        (ulx, uly, ulz) = tx.TransformPoint(crsTransform[0], crsTransform[3])
        (lrx, lry, lrz) = tx.TransformPoint(crsTransform[0] + crsTransform[1] * x_size,
                                            crsTransform[3] + crsTransform[5] * y_size)

        # create file in memory
        mem_dataset = gdal.GetDriverByName('MEM')

        # calculate new properties output result
        if scale:
            new_x, new_y = int((lrx - ulx) / scale), int((uly - lry) / scale)
            dest = mem_dataset.Create('', new_x, new_y, 1, gdal.GDT_Float32)
            crsTransform = (ulx, scale, crsTransform[2], uly, crsTransform[4], -scale)
        else:
            new_x, new_y = int(lrx - ulx), int(uly - lry)
            dest = mem_dataset.Create('', new_x, new_y, 1, gdal.GDT_Float32)

        dest.SetGeoTransform(crsTransform)
        dest.SetProjection(crs_to.ExportToWkt())

        gdal.ReprojectImage(dataset, dest, crs_from.ExportToWkt(), crs_to.ExportToWkt(), gdal.GRA_NearestNeighbour)

        return dest

    @staticmethod
    def get_extent_of_feat(feat):
        geom = feat.GetGeometryRef()
        if geom.GetGeometryName() == 'MULTIPOLYGON':
            pointsX = []
            pointsY = []
            for polygon in geom:
                ring = polygon.GetGeometryRef(0)
                numpoints = ring.GetPointCount()
                for p in range(numpoints):
                    lon, lat, z = ring.GetPoint(p)
                    pointsX.append(lon)
                    pointsY.append(lat)
        elif geom.GetGeometryName() == 'POLYGON':
            ring = geom.GetGeometryRef(0)
            numpoints = ring.GetPointCount()
            pointsX = []
            pointsY = []
            for p in range(numpoints):
                lon, lat, z = ring.GetPoint(p)
                pointsX.append(lon)
                pointsY.append(lat)
        else:
            raise Exception("Geometry is not a Polygon or Multipolygon")
        return pointsX, pointsY

    @staticmethod
    def get_extent_coords(pointsX, pointsY):
        xmin = min(pointsX)
        xmax = max(pointsX)
        ymin = min(pointsY)
        ymax = max(pointsY)
        return xmin, xmax, ymin, ymax

    @staticmethod
    def specify_offset_of_rows_and_columns(xmin, xmax, ymin, ymax, x_origin, y_origin, pixel_width):
        xoff = int((xmin - x_origin) / pixel_width)
        yoff = int((y_origin - ymax) / pixel_width)
        xcount = int((xmax - xmin) / pixel_width) + 1
        ycount = int((ymax - ymin) / pixel_width) + 1
        return xoff, yoff, xcount, ycount
