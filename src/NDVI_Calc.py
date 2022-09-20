import datetime
import os

import gdal
import matplotlib.pyplot as plt
import numpy


class NDVI_Calc(object):

    def createOutputImage(self, outFileName, inDataset):
        driver = inDataset.GetDriver()

        geoTransform = inDataset.GetGeoTransform()
        geoProj = inDataset.GetProjection()

        newDataset = driver.Create(outFileName, inDataset.RasterXSize, inDataset.RasterYSize, 1, gdal.GDT_Float32)

        print("opened file")
        newDataset.SetGeoTransform(geoTransform)
        newDataset.SetProjection(geoProj)

        return newDataset

    def calcNDVI(self, redFilePath, niFilePath, outFilePath):

        redDS = gdal.Open(redFilePath, gdal.GA_ReadOnly)
        redBand = redDS.GetRasterBand(1)

        x = redDS.GetGeoTransform()[0]
        y = redDS.GetGeoTransform()[3]

        niDS = gdal.Open(niFilePath, gdal.GA_ReadOnly)
        niBand = niDS.GetRasterBand(1)

        rows = redBand.YSize
        cols = redBand.XSize

        ndviDS = self.createOutputImage(outFilePath + ".tif", redDS)
        print('reading file...')

        if ndviDS == None:
            print("Error: Invalid output file")

        ndvi = []

        print('proccessing image...')

        for i in range(rows):
            red = redBand.ReadAsArray(0, i, cols, 1).astype(numpy.float32)
            # red = numpy.array(red, dtype=numpy.float32)

            ni = niBand.ReadAsArray(0, i, cols, 1).astype(numpy.float32)
            # ni = numpy.array(ni, dtype=numpy.float32)

            ndviRow = []

            for j in range(cols):
                numerator = ni[0][j] - red[0][j]
                denominator = ni[0][j] + red[0][j]

                if denominator != 0:
                    ndviRow.append(numerator / denominator)
                else:
                    ndviRow.append(0.0)
            ndvi.append(ndviRow)

        ndviDS.GetRasterBand(1).WriteArray(numpy.array(ndvi))
        ndviDS.GetRasterBand(1).SetNoDataValue(-999)

        im = plt.imshow(ndvi, cmap='RdYlGn')

        plt.colorbar(im, fraction=0.02)
        plt.savefig(outFilePath + ".png")

        # ndviDS.GetRasterBand(1).SetNoDataValue(-999)
        print("File Saved...")
        ndviDS.FlushCache()

        ndviDS = None

        del ndvi, ndviDS

    def run(self, redFilePath, niFilePath):
        outFilename = str(datetime.datetime.now().date()) + '_' + str(
            datetime.datetime.now().time()).replace(':', '.') + "_ndvi"

        outFilePath = "static\\NDVI_Images" + os.sep + outFilename

        if os.path.exists(redFilePath) and os.path.exists(niFilePath):
            self.calcNDVI(redFilePath, niFilePath, outFilePath)
        else:
            print("Error: File not found")

        return outFilename
