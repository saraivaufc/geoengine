import ee

# fc = ee.FeatureCollection("data/LANDSAT.shp")

# ee.batch.Export.table.toDatabase(
#     collection=fc,
#     fileNamePrefix="LANDSAT/LX/WRS"
# )


fc = ee.FeatureCollection("data/SENTINEL.shp")

ee.batch.Export.table.toDatabase(
    collection=fc,
    fileNamePrefix="COPERNICUS/S2/TILES"
)
