from osgeo import ogr, osr


# Methods to create and read shape files


# creates a polygon shapefile using geographic long and lat coordinates
def createPolygon(polyPoints):
    ring = ogr.Geometry(ogr.wkbLinearRing)

    # writes each point into the shapefile
    for shapePoint in polyPoints:
        ring.AddPoint(shapePoint[1], shapePoint[0])

    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)

    return poly.ExportToWkt()


def writeShapefile(poly, filename):
    spatialRef = osr.SpatialReference()
    # defines the spatial reference to be wgs84
    spatialRef.ImportFromEPSG(4326)

    driver = ogr.GetDriverByName('Esri Shapefile')
    shpDS = driver.CreateDataSource("static\\Shape Files\\" + filename)
    layer = shpDS.CreateLayer('shape', spatialRef, ogr.wkbPolygon)

    layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
    defn = layer.GetLayerDefn()

    feat = ogr.Feature(defn)
    feat.SetField('id', 123)

    geom = ogr.CreateGeometryFromWkt(poly)
    geom.AssignSpatialReference(spatialRef)
    feat.SetGeometry(geom)
    spatialRef.ExportToWkt()

    layer.CreateFeature(feat)

    shpDS.Destroy()


# reads a shapefile and produces a projection file
def readShape(filename):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shapeFile = driver.Open("static\\Shape Files\\" + filename)
    layer = shapeFile.GetLayer()
    spatialRef = layer.GetSpatialRef()
    spatialRef.ExportToWkt()

    driver = None
    shapeFile.Destroy()
