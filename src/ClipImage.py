import fiona
import rasterio.mask
from osgeo import osr, gdal, ogr

shapeFilePath = "static\\Shape Files\\"
imgFilepath = "static\\NDVI_Images\\"
imgFilename="uchill_mica_index_ndvi.tif"


def checkSpatialRef(shapeFile):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    shapeDS = driver.Open(shapeFile+"\\shape.shp", 1)
    layer = shapeDS.GetLayer()
    shapePrj = layer.GetSpatialRef()
 
    # current spatial reference
    shapeSpRef = shapePrj.GetAttrValue('authority', 1)
    print(shapeSpRef)

    tif = gdal.Open(imgFilepath+imgFilename)
    imgSpRef = getImgProj(imgFilepath+imgFilename)

    if int(shapeSpRef) != imgSpRef:
        targetPrj = osr.SpatialReference()
        targetPrj.ImportFromEPSG(32617)
        transfrom = osr.CoordinateTransformation(shapePrj, targetPrj)

        to_fill = ogr.GetDriverByName("Esri Shapefile")
        newShapeDS = to_fill.CreateDataSource(shapeFile+"reprj")
        outLayer = newShapeDS.CreateLayer('shape', targetPrj, ogr.wkbPolygon)
        outLayer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))

        for feature in layer:
            pt = feature.GetGeometryRef()
            pt.Transform(transfrom)

            geom = ogr.CreateGeometryFromWkt(pt.ExportToWkt())
            geom.AssignSpatialReference(targetPrj)
            defn = outLayer.GetLayerDefn()
            feat = ogr.Feature(defn)
            feat.SetField('id', 123)
            feat.SetGeometry(geom)
            targetPrj.ExportToWkt()
            outLayer.CreateFeature(feat)
            feat = None

        newLayer = newShapeDS.GetLayer()
        newShapePrj = newLayer.GetSpatialRef()
        newShapeSpRef = newShapePrj.GetAttrValue('authority', 1)
        print(newShapeSpRef)
        newShapeDS.Destroy()
        return True


def getImgProj(imgFile):
    src = gdal.Open(imgFile)
    prj = src.GetProjection()
    srs = osr.SpatialReference(wkt=prj)
    print(srs.GetAttrValue('authority', 1))

    return int(srs.GetAttrValue('authority', 1))

    # convert utm coordinates to wgs84


def clip(shapeFilename):
    runn=checkSpatialRef(shapeFilePath+shapeFilename)
    if runn==True:
        with fiona.open(shapeFilePath+shapeFilename+"reprj\\shape.shp", "r") as shapefile:
            features = [feature["geometry"] for feature in shapefile]
        with rasterio.open(imgFilepath+imgFilename) as src:
            out_image, out_transform = rasterio.mask.mask(src, features,
                                                          crop=True)
            out_meta = src.meta.copy()
        out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform})
        with rasterio.open("static\\NDVI_Images_Masked\\masked-"+imgFilename, "w", **out_meta) as dest:
            dest.write(out_image)
