import ee

fc = ee.FeatureCollection("data/table.shp")

ee.batch.Export.table.toDatabase(
    collection=fc,
    fileNamePrefix="TABLE"
)
