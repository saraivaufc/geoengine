import functools

import ge.apifunction
import ge.ee_list
import ge.element


class Collection(ge.element.Element):
    def __init__(self, features, *args, **kwargs):
        super(Collection, self).__init__(
            ge.apifunction.ApiFunction.lookup('Collection.load'), kwargs)
        self._features = features
        self.__dict__.update(kwargs)

    def map(self, algorithm, dropNulls=False):
        print("Collection.map")
        collection = self.copy()
        collection._features = ge.ee_list.List(
            map(lambda x: algorithm(x), collection._features))
        return collection

    def reduce(self, reducer, parallelScale):
        print("Collection.reduce")
        element = functools.reduce(lambda x, y: reducer(x, y), self._features)
        return element

    def first(self):
        return self._features[0]

    def last(self):
        return self._features[-1]

    def size(self):
        return len(self._features)

    def toList(self, count, offset=0):
        return self.limit(count)

    def limit(self, max, property=None, ascending=True):
        return self._features[:max]

    def copy(self):
        return Collection(self._features, **self.__dict__)

    @staticmethod
    def name():
        return 'Collection'
