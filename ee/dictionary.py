#!/usr/bin/env python
"""A wrapper for dictionaries."""

import ee.computedobject


class Dictionary(ee.computedobject.ComputedObject):

    def __init__(self, dict={}, **kwargs):
        self._dictionary = dict
        self.__dict__.update(kwargs)

    def get(self, key):
        return self._dictionary.get(key)

    def set(self, key, value):
        dictionary = self.copy()
        dictionary._dictionary[key] = value
        return dictionary

    def keys(self):
        return self._dictionary.keys()

    @staticmethod
    def name():
        return 'Dictionary'

    def encode(self, opt_encoder=None):
        if self._dictionary is not None:
            return opt_encoder(self._dictionary)
        else:
            return super(Dictionary, self).encode(opt_encoder)

    def copy(self):
        return Dictionary(self._dictionary, **self.__dict__)

    def getInfo(self):
        return self._dictionary
