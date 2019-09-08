#!/usr/bin/env python
"""Base class for Image, Feature and Collection.

This class is never intended to be instantiated by the user.
"""

import ge.apifunction
import ge.computedobject
import ge.dictionary
import ge.ee_exception


class Element(ge.computedobject.ComputedObject):
    """Base class for ImageCollection and FeatureCollection."""

    _initialized = False

    def __init__(self, func, args, opt_varName=None):
        """Constructs a collection by initializing its ComputedObject."""
        super(Element, self).__init__(func, args, opt_varName)
        self._id = None
        self._properties = ge.dictionary.Dictionary({})

    @staticmethod
    def name():
        return 'Element'

    def set(self, *args):
        """Overrides one or more metadata properties of an Element.

        Args:
          *args: Either a dictionary of properties, or a vararg sequence of
              properties, e.g. key1, value1, key2, value2, ...

        Returns:
          The element with the specified properties overridden.
        """
        if len(args) == 1:
            properties = args[0]

            # If this is a keyword call, unwrap it.
            if (isinstance(properties, dict) and
                    (len(properties) == 1 and 'properties' in properties) and
                    isinstance(properties['properties'],
                               (dict, ge.computedobject.ComputedObject))):
                # Looks like a call with keyword parameters. Extract them.
                properties = properties['properties']

            if isinstance(properties, dict):
                # Still a plain object. Extract its keys. Setting the keys separately
                # allows filter propagation.
                result = self
                for key, value in properties.items():
                    result = ge.apifunction.ApiFunction.call_(
                        'Element.set', result, key, value)
            elif (isinstance(properties, ge.computedobject.ComputedObject) and
                  ge.apifunction.ApiFunction.lookupInternal(
                      'Element.setMulti')):
                # A computed dictionary. Can't set each key separately.
                result = ge.apifunction.ApiFunction.call_(
                    'Element.setMulti', self, properties)
            else:
                raise ge.ee_exception.EEException(
                    'When Element.set() is passed one argument, '
                    'it must be a dictionary.')
        else:
            # Interpret as key1, value1, key2, value2, ...
            if len(args) % 2 != 0:
                raise ge.ee_exception.EEException(
                    'When Element.set() is passed multiple arguments, there '
                    'must be an even number of them.')
            result = self
            for i in range(0, len(args), 2):
                key = args[i]
                value = args[i + 1]
                result._properties.set(key, value)

        return self._cast(result)

    def get(self, property):
        return self._properties.get(property)

    def properties(self):
        return self._properties

    def copyProperties(self, source, properties=None, exclude=None):
        """
        Incomplete
        :param source:
        :param properties:
        :param exclude:
        :return:
        """
        element = self.copy()
        element._properties = source._properties
        return element
