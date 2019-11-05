import functools

import ge.computedobject


class List(ge.computedobject.ComputedObject):
    def __init__(self, elements=[], **kwargs):
        self._elements = list(elements)
        self.__dict__.update(kwargs)

    def add(self, element):
        list = self.copy()
        list._elements.append(element)
        return list

    def get(self, index):
        return self._elements[index]

    def iterate(self, function, first):
        pass

    def reduce(self, reducer):
        from ge.image import Image, Band
        first_element = self._elements[0]
        if isinstance(first_element, Image):
            new_image = Image()
            new_image = first_element.copyProperties(new_image)
            for band_index, band in enumerate(first_element.getBands()):
                band_data = []

                for image in self._elements:
                    image_band = image.getBands().get(band_index)
                    band_data.append(image_band.getData())

                band_data = functools.reduce(lambda x, y: reducer(x, y),
                                             band_data)
                new_band = Band(name=band.getName(), type=band.getType(),
                                data=band_data)
                new_band = band.copyProperties(new_band)
                new_image = new_image.addBand(new_band)
            return new_image
        else:
            element = functools.reduce(lambda x, y: reducer(x, y),
                                       self._elements)
            return element

    def insert(self, index, element):
        list = self.copy()
        list._elements[index] = element
        return list

    def length(self):
        return len(self._elements)

    def slice(self, start, end):
        list = self.copy()
        list._elements = self._elements[start: end]
        return list

    def __iter__(self):
        return iter(self._elements)

    def copy(self):
        return List(self._elements, **self.__dict__)

    def encode(self, opt_encoder=None):
        if self._elements is not None:
            return opt_encoder(self._elements)
        else:
            return super(List, self).encode(opt_encoder)

    @staticmethod
    def name():
        return 'List'
