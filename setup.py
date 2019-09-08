# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='geoengine',
    version='0.0.1',
    url='https://github.com/saraivaufc/earth-engine.git',
    author='Marciano Saraiva',
    author_email='saraiva.ufc@gmail.com',
    keywords='remote sensing,geoprocessing',
    description=u"Earth Engine combines a multi-petabyte catalog of satellite imagery and geospatial datasets with planetary-scale analysis capabilities and makes it available for scientists, researchers, and developers to detect changes, map trends, and quantify differences on the Earth's surface.",
    packages=['ge'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
)