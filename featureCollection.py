import ge

# fc = ge.FeatureCollection("data/LANDSAT.shp")
#
# ge.batch.Export.table.toDatabase(
#     collection=fc,
#     fileNamePrefix="LANDSAT/WRS"
# )

geometry = ge.Geometry('{"type": "MultiPolygon", "coordinates": [ [ [ [ '
                       '-46.208235865545305, -13.156115482264447 ], [ -46.248416270501231, -13.195654332679714 ], [ -46.168055460589386, -13.206890523634273 ], [ -46.163353498307302, -13.159445315873686 ], [ -46.207380963312204, -13.156947944907824 ], [ -46.208235865545305, -13.156115482264447 ] ] ] ] }')

fc = ge.FeatureCollection("db://LANDSAT/WRS") \
    .filterBounds(geometry)

tiles = []
for f in fc.toList(12):
    print(f.properties())
    tiles.append(f.get("path"))
print(tiles)

# fc = ge.FeatureCollection("data/SENTINEL.shp")
#
# ge.batch.Export.table.toDatabase(
#     collection=fc,
#     fileNamePrefix="COPERNICUS/S2/TILES"
# )
