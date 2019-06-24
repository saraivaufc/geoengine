import ee

image = ee.Image("data/image.tif")

ee.Export.image.toDatabase(
    image=image.float(),
    fileNamePrefix="LANDSAT/LC08/C01/T1_TOA/image.tif"
)

# image = ee.Image("db:LANDSAT/LC08/C01/T1_TOA/image.tif") \
#     .select(['b1', 'b2', 'b3', 'b4', 'b5', 'b6'],
#             ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2'])
#
# ndvi = image.normalizedDifference(["NIR", "RED"]).rename("NDVI")
#
# ee.Export.image.toLocalDisk(ndvi.toFloat32(), "ndvi.tif")

