import tensorflow as tf


class Reducer(object):
    @staticmethod
    def sum():
        return tf.reduce_sum

    @staticmethod
    def min():
        return tf.reduce_min

    @staticmethod
    def max():
        return tf.reduce_max

    @staticmethod
    def mean():
        return tf.reduce_mean

    @staticmethod
    def name():
        return 'Reduce'
