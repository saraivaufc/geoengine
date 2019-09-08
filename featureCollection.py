import ge

# fc = ee.FeatureCollection("data/LANDSAT.shp")

# ee.batch.Export.table.toDatabase(
#     collection=fc,
#     fileNamePrefix="LANDSAT/LX/WRS"
# )


fc = ge.FeatureCollection("data/SENTINEL.shp")

ge.batch.Export.table.toDatabase(
    collection=fc,
    fileNamePrefix="COPERNICUS/S2/TILES"
)
