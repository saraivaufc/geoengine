import json
import os
import tempfile
import random
from ge.db import models

from osgeo import gdal, osr, ogr

class Export():
    class image(object):
        @staticmethod
        def toLocalDisk(image, fileNamePrefix):
            dataset = Export.image.__build_dataset(image)
            print("imagem computada com sucesso")

            gdal.Translate(fileNamePrefix, dataset, format='GTiff')

            print("imagem salva com sucesso")

        @staticmethod
        def toDatabase(image, fileNamePrefix):
            dataset = Export.image.__build_dataset(image)
            print("imagem computada com sucesso")

            words = fileNamePrefix.split("/")

            filename = words[-1]
            imageCollectionPath = "/".join(words[0:-1])

            models.ImageCollection.objects(path=imageCollectionPath) \
                .update_one(upsert=True, set__path=imageCollectionPath)

            imageCollection = models.ImageCollection\
                .objects(path=imageCollectionPath)\
                .first()

            models.Image.objects(
                imageCollection=imageCollection.id,
                path=filename,
            ).update_one(upsert=True,
                set__imageCollection=imageCollection.id,
                set__path=filename,
                properties=image.properties().getInfo()
            )

            image = models.Image.objects(imageCollection=imageCollection.id,
                                         path=filename).first()

            with tempfile.TemporaryDirectory() as tmpdirname:
                tmpfilename = "{dir}{sep}{filename}".format(
                    dir=tmpdirname,
                    sep=os.sep,
                    filename=filename
                )
                gdal.Translate(tmpfilename, dataset, format='GTiff')
                file = open(tmpfilename, "rb")
                image.file.replace(file, content_type='image/tiff')
                image.save()

        @staticmethod
        def __build_dataset(image):
            image = image.getInfo()

            fileNamePrefix = "/vsimem/{hash}".format(
                hash=random.getrandbits(128))
            first_band = image.getBands().get(0)
            cols = first_band.getCols()
            rows = first_band.getRows()
            projection = first_band.getCRS()
            transform = first_band.getTransform()
            band_type = first_band.getType()


            print("Exporting file with:\n"
                  "Cols:{cols}\n"
                  "Rows:{rows}\n"
                  "Projection:{projection}\n"
                  "Transform:{transform}\n"
                  "Type:{band_type}".format(cols=cols,
                                       rows=rows,
                                       projection=str(projection),
                                       transform=str(transform),
                                       band_type=str(band_type)))

            driver = gdal.GetDriverByName('MEM')

            dataset = driver.Create(
                fileNamePrefix,
                cols,
                rows,
                image.getBands().length(),
                band_type
            )

            dataset.SetGeoTransform(transform)
            dataset.SetProjection(projection)
            for band_index, band in enumerate(image.getBands()):
                print("***********************************")
                print("Cols: {} Rows: {}".format(band.getCols(),
                                                 band.getRows()))
                print("***********************************")
                dataset.GetRasterBand(band_index + 1).WriteArray(band.getData())
            return dataset

        @staticmethod
        def name():
            return 'Export.image'

    class table(object):
        @staticmethod
        def toLocalDisk(collection, fileNamePrefix):
            collection = collection.getInfo()
            Export.table.__build_dataset(collection, fileNamePrefix)

        @staticmethod
        def toDatabase(collection, fileNamePrefix=None, **kwargs):
            models.FeatureCollection \
                .objects(code=fileNamePrefix) \
                .update_one(upsert=True, set__code=fileNamePrefix)

            featureCollection = models.FeatureCollection\
                .objects(code=fileNamePrefix)\
                .first()

            for feature in collection.features():
                geometry = json.loads(feature.geometry().toGeoJSON())
                properties = feature.properties().getInfo()
                print(properties)

                feature = models.Feature(
                    featureCollection=featureCollection,
                    geometry=geometry,
                    properties=properties
                )
                feature.save()

        @staticmethod
        def __build_dataset(collection, fileNamePrefix):
            driver = ogr.GetDriverByName("ESRI Shapefile")
            data_source = driver.CreateDataSource(fileNamePrefix)

            srs = osr.SpatialReference()
            srs.ImportFromEPSG(4326)

            data_source.CreateLayer("volcanoes", srs, ogr.wkbPoint)
            data_source.Destroy()

        @staticmethod
        def name():
            return 'Export.image'

    @staticmethod
    def name():
        return 'Export'