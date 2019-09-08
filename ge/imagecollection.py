import functools

from ge.collection import Collection


class ImageCollection(Collection):
    def __init__(self, features, *args, **kwargs):
        super(ImageCollection, self).__init__(features, args, kwargs)

    @staticmethod
    def load(id, version):
        pass

    def reduce(self, reducer, parallelScale=None):
        from ge.image import Image, Band
        first_image = self.first()
        new_image = Image()
        new_image = first_image.copyProperties(new_image)
        for band_index, band in enumerate(first_image.getBands()):
            band_data = []

            for image in self.toList(5000):
                image_band = image.getBands().get(band_index)
                band_data.append(image_band.getData())

            band_data = functools.reduce(lambda x, y: reducer(x, y), band_data)
            new_band = Band(name=band.getName(), type=band.getType(),
                            data=band_data)
            new_image = new_image.addBand(new_band)
        return new_image

    @staticmethod
    def name():
        return 'ImageCollection'

    @staticmethod
    def elementType():
        return Image
