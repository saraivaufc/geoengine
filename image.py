import ge

image = ge.Image("data/image.tif")

ge.Export.image.toDatabase(
    image=image.float(),
    fileNamePrefix="LANDSAT/LC08/C01/T1_TOA/image.tif"
)

# image = ge.Image("db://LANDSAT/LC08/C01/T1_TOA/image.tif") \
#     .select(['B1', 'B2', 'B3', 'B4', 'B5', 'B6'],
#             ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2'])
#
# ndvi = image.normalizedDifference(["NIR", "RED"]).rename("NDVI")
#
# ge.Export.image.toLocalDisk(ndvi.toFloat32(), "data/ndvi.tif")