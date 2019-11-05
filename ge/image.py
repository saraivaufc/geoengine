import gc
import random
from urllib.parse import urlparse

import numpy as np
import tensorflow as tf
from osgeo import gdal
from osgeo import gdal_array

import ge.apifunction
import ge.ee_list
import ge.element
from ge.db import models
from ge.tools import Raster


# https://pcjericks.github.io/py-gdalogr-cookbook/

class Image(ge.element.Element):
    def __init__(self, *args, **kwargs):
        super(Image, self).__init__(
            ge.apifunction.ApiFunction.lookup('Image.load'), kwargs)

        self._bands = ge.ee_list.List([])
        self.__dict__.update(kwargs)

        if len(args) > 0:
            if isinstance(args[0], str):
                image = self.load(args[0])
                self._id = image._id
                self._bands = image._bands
                self._properties = image._properties
            elif isinstance(args[0], int) or isinstance(args[0], float):
                image = self.constant(args[0])
                self._id = image._id
                self._bands = image._bands
                self._properties = image._properties

    @staticmethod
    def load(id):
        id = urlparse(id)

        if id.scheme == "db":
            image = Image._loadFromDatabase(id.netloc + id.path)
        else:
            image = Image._loadFromLocalDisk(id.path)
        return image

    @staticmethod
    def constant(value):
        image = Image()
        image._id = "constant"

        if isinstance(value, int):
            image_type = gdal.GDT_Int16
        elif isinstance(value, float):
            image_type = gdal.GDT_Float32
        else:
            image_type = gdal.GDT_Float32
        band = Band(name=image._id, type=image_type,
                    data=tf.convert_to_tensor(value))
        image._bands = image._bands.add(band)
        return image

    @staticmethod
    def _loadFromLocalDisk(id):
        image = Image()
        image._id = id

        dataSource = gdal.Open(id)

        for index in range(1, dataSource.RasterCount + 1):
            band_name = "B{band_number}".format(band_number=index)
            band_data = dataSource.GetRasterBand(index).ReadAsArray()

            band_type = band_data.dtype
            if isinstance(band_type, int):
                band_type = gdal.GDT_Int16
            elif isinstance(band_type, float):
                band_type = gdal.GDT_Float32
            else:
                band_type = gdal.GDT_Float32

            band = Band(name=band_name, type=band_type, data=band_data)
            band = band.setCols(dataSource.RasterXSize)
            band = band.setRows(dataSource.RasterYSize)
            band = band.setCRS(dataSource.GetProjectionRef())
            band = band.setTransform(dataSource.GetGeoTransform())
            print("Band {count} carregada!".format(count=index))

            image._bands = image._bands.add(band)

        return image

    @staticmethod
    def _loadFromDatabase(dataSourceNamePrefix):
        print("dataSourceNamePrefix:", dataSourceNamePrefix)
        words = dataSourceNamePrefix.split("/")

        filename = words[-1]
        print("filename:", filename)
        imageCollectionPath = "/".join(words[0:-1])

        print("imageCollectionPath:", imageCollectionPath)

        imageCollection = models.ImageCollection \
            .objects(path=imageCollectionPath) \
            .first()

        if imageCollection:
            image = models.Image.objects(imageCollection=imageCollection.id,
                                         path=filename).first()

            if image:
                filename = "/vsimem/{hash}".format(
                    hash=random.getrandbits(128))
                gdal.FileFromMemBuffer(filename, image.file.read())
                return Image._loadFromLocalDisk(filename)
            else:
                raise FileNotFoundError("Image not found")
        else:
            raise FileNotFoundError("Collection not found")

    def addBands(self, image2, names=True, overwrite=True):
        """
        Returns an image containing all bands copied from the first input and selected bands from the second input, optionally overwriting bands in the first image with the same name. The new image has the metadata and footprint from the first input image.

        Arguments:
        this:dstImg (Image):
        An image into which to copy bands.

        srcImg (Image):
        An image containing bands to copy.

        names (List, default: null):
        Optional list of band names to copy. If names is omitted, all bands from srcImg will be copied over.

        overwrite (Boolean, default: false):
        If true, bands from srcImg will override bands with the same names in dstImg. Otherwise the new band will be renamed with a numerical suffix ('foo' to 'foo_1' unless 'foo_1' exists, then 'foo_2' unless it exists, etc).
        """
        image = self.copy()
        for band in image2._bands:
            image._bands = image._bands.add(band)
        return image

    def getBands(self):
        return self._bands

    def metadata(self, property, name):
        """
        Generates a constant image of type double from a metadata property.
        """
        image = self.copy()
        image = image.set(property, name)
        return image

    def bandNames(self):
        names = []
        for band in self._bands:
            names.append(band.getName())
        return names

    def add(self, image2):
        return self.applyFunc(ge.Image(image2), tf.math.add)

    def multiply(self, image2):
        return self.applyFunc(ge.Image(image2), tf.math.multiply)

    def subtract(self, image2):
        return self.applyFunc(ge.Image(image2), tf.math.subtract)

    def divide(self, image2):
        return self.applyFunc(ge.Image(image2), tf.math.divide)

    def eq(self, image2):
        return self.applyFunc(ge.Image(image2), tf.math.equal)

    def gt(self, image2):
        return self.applyFunc(ge.Image(image2), tf.math.greater)

    def gte(self, image2):
        return self.applyFunc(ge.Image(image2), tf.math.greater_equal)

    def lt(self, image2):
        return self.applyFunc(ge.Image(image2), tf.math.less)

    def lte(self, image2):
        return self.applyFunc(ge.Image(image2), tf.math.less_equal)

    def matrixMultiply(self, image2):
        return self.applyFunc(ge.Image(image2), tf.math.matmul)

    def max(self, image2):
        return self.applyFunc(ge.Image(image2), tf.math.maximum)

    def min(self, image2):
        return self.applyFunc(ge.Image(image2), tf.math.minimum)

    def neq(self, image2):
        return self.applyFunc(ge.Image(image2), tf.math.not_equal)

    def exp(self):
        return self.applyFuncMono(tf.math.exp)

    def log(self):
        return self.applyFuncMono(tf.math.log)

    def rename(self, var_args=[]):
        if isinstance(var_args, str):
            var_args = [var_args]
        image = self.copy()
        for band_index, band_name in enumerate(var_args):
            band = self._bands.get(band_index)
            image._bands = image._bands.insert(band_index,
                                               band.setName(band_name))
        return image

    def toInt16(self):
        image = self.copy()
        bands = ge.ee_list.List([])
        for band_index, band in enumerate(image._bands):
            band = band.setType(gdal.GDT_Int16)
            bands = bands.add(band)
        image._bands = bands
        return image

    def int(self):
        return self.toInt16()

    def toFloat32(self):
        image = self.copy()
        bands = ge.ee_list.List([])
        for band_index, band in enumerate(image._bands):
            band = band.setType(gdal.GDT_Float32)
            bands = bands.add(band)
        image._bands = bands
        return image

    def float(self):
        return self.toFloat32()

    def projection(self):
        """
        return the project of first band
        """
        first_band = self._bands.get(0)
        proj = ge.Projection(crs=first_band.getCRS(),
                             transform=first_band.getTransform())
        return proj

    def reduce(self, image2, function):
        pass

    def select(self, opt_selectors=[], opt_names=[]):
        opt_selectors = [opt_selectors] if not isinstance(opt_selectors,
                                                          list) else opt_selectors
        image = self.copy()
        bands = image._bands
        new_bands = ge.List([])
        for index, selector in enumerate(opt_selectors):
            new_band = None
            if isinstance(selector, str):
                for band in bands:
                    if band.getName() == selector:
                        new_band = band
                        break

            if new_band is None:
                raise Exception("Band {band_name} not found in image.".format(
                    band_name=selector))

            if len(opt_names) > 0:
                new_bands = new_bands.add(new_band.setName(opt_names[index]))
            else:
                new_bands = new_bands.add(new_band)

        image._bands = new_bands
        return image

    def normalizedDifference(self, bandNames=None):
        image = self.copy()
        first = image.select(bandNames[0])
        second = image.select(bandNames[1])
        normDifference = first.subtract(second).divide(first.add(second))
        return normDifference

    def applyFunc(self, image2, func):
        new_image = Image()
        new_image = new_image.copyProperties(self)

        if self._bands.length() == image2._bands.length():
            for index, band in enumerate(self._bands):
                band2 = image2._bands.get(index)
                new_band = band.applyFunc(band2, func)
                new_image._bands = new_image._bands.add(new_band)

        elif self._bands.length() > 1 and image2._bands.length() == 1:
            for band in self._bands:
                for band2 in image2._bands:
                    new_band = band.applyFunc(band2, func)
                    new_image._bands = new_image._bands.add(new_band)

        elif self._bands.length() == 1 or image2._bands.length() > 1:
            for band2 in image2._bands:
                for band in self._bands:
                    new_band = band.applyFunc(band2, func)
                    new_image._bands = new_image._bands.add(new_band)
        else:
            raise IndexError("Band index error")

        return new_image

    def applyFuncMono(self, func):
        new_image = Image()
        new_image = new_image.copyProperties(self)

        for index, band in enumerate(self._bands):
            new_band = band.applyFuncMono(func)
            new_image._bands = new_image._bands.add(new_band)

        return new_image

    def reproject(self, crs=None, crsTransform=None, scale=None):
        if not crs:
            crs = self.projection().crs()
        if crsTransform and scale:
            raise ValueError("crsTransform and scale cannot both be value.")

        image = self.copy().getInfo()
        bands = ge.ee_list.List([])
        for band_index, band in enumerate(image._bands):
            band_reprojected = band.reproject(crs, crsTransform, scale)
            bands = bands.add(band_reprojected)
        image._bands = bands
        return image

    def clip(self, geometry):
        image = self.copy().getInfo()
        bands = ge.ee_list.List([])
        for band_index, band in enumerate(image._bands):
            band_clipped = band.clip(geometry)
            bands = bands.add(band_clipped)
        image._bands = bands
        return image

    def getInfo(self):
        image = self.copy()
        bands = ge.ee_list.List([])
        for band_index, band in enumerate(image._bands):
            band = band.getInfo()
            bands = bands.add(band)
        image._bands = bands
        return image

    def copy(self):
        return Image(self.args, **self.__dict__)

    def copyProjection(source):
        metadata

    @staticmethod
    def name():
        return 'Image'


class Band(ge.element.Element):
    def __init__(self, name, type, data=None, **kwargs):
        super(Band, self).__init__(
            ge.apifunction.ApiFunction.lookup('Image.band'), kwargs)
        self._name = name
        self._cols = None
        self._rows = None
        self._crs = None
        self._transform = None
        self._type = type
        self._data = data
        self.__dict__.update(kwargs)

    def getName(self):
        return self._name

    def getCols(self):
        return self._cols

    def getRows(self):
        return self._rows

    def getCRS(self):
        return self._crs

    def getTransform(self):
        return self._transform

    def getType(self):
        return self._type

    def getData(self):
        return self._data

    def setName(self, name):
        band = self.copy()
        band._name = name
        return band

    def setCols(self, cols):
        band = self.copy()
        band._cols = cols
        return band

    def setRows(self, rows):
        band = self.copy()
        band._rows = rows
        return band

    def setCRS(self, crs):
        band = self.copy()
        band._crs = crs
        return band

    def setTransform(self, transform):
        band = self.copy()
        band._transform = transform
        return band

    def setType(self, type):
        band = self.copy()
        band._type = type
        return band

    def setData(self, data):
        band = self.copy()
        band._data = data
        return band

    @property
    def _gdal_dataset(self):
        transform = self.getTransform()
        projection = self.getCRS()

        dataset = gdal_array.OpenArray(self.getData())
        dataset.SetGeoTransform(transform)
        dataset.SetProjection(projection)
        return dataset

    def applyFunc(self, band2, func):
        a = tf.cast(self.getData(), tf.float32)
        b = tf.cast(band2.getData(), tf.float32)
        c = func(a, b)
        new_band = Band(name=self.getName(), type=self.getType(), data=c) \
            .setCols(self.getCols()) \
            .setRows(self.getRows()) \
            .setCRS(self.getCRS()) \
            .setTransform(self.getTransform())
        new_band = new_band.copyProperties(self)
        return new_band

    def applyFuncMono(self, func):
        a = tf.cast(self.getData(), tf.float32)
        c = func(a)

        new_band = Band(name=self.getName(), type=self.getType(), data=c) \
            .setCols(self.getCols()) \
            .setRows(self.getRows()) \
            .setCRS(self.getCRS()) \
            .setTransform(self.getTransform())
        new_band = new_band.copyProperties(self)
        return new_band

    def reproject(self, crs, crsTransform=None, scale=None):
        dataset = self._gdal_dataset

        dataset_reprojected = Raster.Reproject(dataset, crs, crsTransform,
                                               scale)
        data = dataset_reprojected.ReadAsArray()

        band = self.copy()
        band = band \
            .setCols(dataset_reprojected.RasterXSize) \
            .setRows(dataset_reprojected.RasterYSize) \
            .setCRS(dataset_reprojected.GetProjectionRef()) \
            .setTransform(dataset_reprojected.GetGeoTransform()) \
            .setData(data)

        return band

    def clip(self, geometry):
        dataset = self._gdal_dataset
        clipped_dataset = Raster.ClipByGeometry(dataset, geometry.toGeoJSON())
        data = clipped_dataset.ReadAsArray()

        band = self.copy()
        band = band \
            .setCols(clipped_dataset.RasterXSize) \
            .setRows(clipped_dataset.RasterYSize) \
            .setCRS(clipped_dataset.GetProjectionRef()) \
            .setTransform(clipped_dataset.GetGeoTransform()) \
            .setData(data)
        return band

    def getInfo(self):
        band = self.copy()
        data = band.getData()
        if type(data) is np.ndarray:
            data = data
        else:
            data = data.numpy()
        band = band.setData(data)
        del data
        gc.collect()
        return band

    def copy(self):
        return Band(self._name, self._type, self._data, **self.__dict__)

    @staticmethod
    def name():
        return 'Band'
