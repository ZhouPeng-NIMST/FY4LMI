#coding:utf-8
#@author : @libin
#@phone  : 010-68400244
#@e_mail : libin033@163.com
#
from osgeo import gdal, gdalnumeric, ogr
from PIL import Image, ImageDraw
import os
import operator
import numpy as np
import shapefile
import netCDF4
import h5py



# def WriteHDF(strfilename, strsdsname, data, overwrite = 1):
#     data = np.array(data)
#     if overwrite == 1:
#         fout = h5py.File(strfilename, 'w')
#     else:
#         fout = h5py.File(strfilename, 'a')
#
#     fout.create_dataset(strsdsname, data=data, dtype= data.dtype)
#     fout.close()
#
#     return 0
#
# def ReadNC(strfilename, strsdsname):
#     if not os.path.isfile(strfilename):
#         print('%s is not exist, will be existed!!!' %strfilename)
#         exit(1)
#     else:
#         fin = netCDF4.Dataset(strfilename, 'r')
#         data = fin.variables[strsdsname][:]
#         fin.close()
#
#         return data

def ImageToArray(i):
    """
    Converts a Python Imaging Library array to a
    gdalnumeric image.
    """
    a=gdalnumeric.fromstring(i.tobytes(),'b')
    a.shape=i.im.size[1], i.im.size[0]
    return a

def World2Pixel(geoMatrix, x, y):
    """
    Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
    the pixel location of a geospatial coordinate
    """
    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = np.fabs(geoMatrix[1])
    yDist = np.fabs(geoMatrix[5])
    rtnX = geoMatrix[2]
    rtnY = geoMatrix[4]

    Pixel = int((x - ulX) / xDist)
    line = int((ulY - y) / yDist)

    return (Pixel, line)


def Calculate_IJ(s_position, in_position, resolution):
    '''
    针对等经纬数据做行列号计算
    :param s_position: 起始点位置
    :param in_position: 输入位置
    :param resolution: 分辨率
    :return: 计算得到的行列号
    '''

    position = np.round(np.fabs(in_position - s_position) / resolution).astype(np.int32)

    return position


def ShapeClipRaster( shapefile_filename,  FLAT, FLON, srcArray, resolutionX=0.25, resolutionY=0.25):
    # Load the source data as a gdalnumeric array
    # srcArray = gdalnumeric.LoadFile(raster_path)

    # Also load as a gdal image to get geotransform
    # (world file) info
    # srcImage, srcGeoTrans, proj = ReadTiff(raster_path)

    # Create an OGR layer from a boundary shapefile
    # shapef = ogr.Open(shapefile_path)
    # lyr = shapef.GetLayer( os.path.split( os.path.splitext( shapefile_path )[0] )[1] )
    # poly = lyr.GetNextFeature()

    # srcArray = ReadNC(raster_filename, "Density")
    # FLAT = ReadNC(raster_filename, "FLAT")
    # FLON = ReadNC(raster_filename, "FLON")

    # resolutionX = 0.25
    # resolutionY = 0.25
    if not os.path.isfile(shapefile_filename):
        print("%s is not exist, will be exit!!!" %shapefile_filename)
        exit(3)
    inShp = shapefile.Reader(shapefile_filename)

    # Convert the layer extent to image pixel coordinates
    # 获取shapefile文件在TIFF文件
    minX, minY, maxX, maxY = inShp.bbox
    print('minX, maxX, minY, maxY:',minX, maxX, minY, maxY)

    # ulX, ulY = World2Pixel(srcGeoTrans, minX, maxY)
    # lrX, lrY = World2Pixel(srcGeoTrans, maxX, minY)

    # 获取区域范围的经纬度
    if minX < np.nanmin(FLON):
        minX = np.nanmin(FLON)
    if maxX > np.nanmax(FLON):
        maxX = np.nanmax(FLON)

    if minY < np.nanmin(FLAT):
        minY = np.nanmin(FLAT)
    if maxY > np.nanmax(FLAT):
        maxY = np.nanmax(FLAT)

    # 计算裁剪区域范围的行列号
    ulX = Calculate_IJ(FLON[0,0], minX, resolutionX)
    ulY = Calculate_IJ(FLAT[0,0], maxY, resolutionY)

    lrX = Calculate_IJ(FLON[0,0], maxX, resolutionX)
    lrY = Calculate_IJ(FLAT[0,0], minY, resolutionY)

    print('ulX, lrX, ulY, lrY:',ulX, lrX, ulY, lrY)
    # Calculate the pixel size of the new image
    # 根据shapefile文件的范围对原始数据进行切片
    pxWidth = int(lrX - ulX)
    pxHeight = int(lrY - ulY)
    print(" pxHeight, pxWidth:", pxHeight, pxWidth)

    if len(srcArray.shape) == 3:
        Level, Row, Pix = srcArray.shape
        clip = srcArray[:, ulY:lrY, ulX:lrX]
    elif len(srcArray.shape) == 2:
        Row, Pix = srcArray.shape
        clip = srcArray[ulY:lrY, ulX:lrX]
    else:
        print("Input Data Dims is not 2 or 3!!!")
        return -1
    # ind = np.where(srcArray == 1e+10 )
    # srcArray[ind] = np.nan
    # clip = srcArray[ulY:lrY, ulX:lrX]*100

    #
    # EDIT: create pixel offset to pass to new image Projection info
    #
    xoffset =  ulX
    yoffset =  ulY
    print("Xoffset, Yoffset = ( %d, %d )" % ( xoffset, yoffset ))

    # Create a new geomatrix for the image
    # 设置GeoTransform 仿射变换函数
    # geoTrans = list(srcGeoTrans)
    # geoTrans[0] = minX
    # geoTrans[3] = maxY

    # Map points to pixels for drawing the
    # boundary on a blank 8-bit,
    # black and white, mask image.
    points = []
    pixels = []
    # geom = poly.GetGeometryRef()
    # pts = geom.GetGeometryRef(0)
    # for p in range(pts.GetPointCount()):
    #     points.append((pts.GetX(p), pts.GetY(p)))
    # for p in points:
    #     pixels.append(World2Pixel(geoTrans, p[0], p[1]))

    # for p in inShp.shape(0).points:
    #     pixels.append(World2Pixel(geoTrans,p[0], p[1]))

    for shape in inShp.shapes():
        partCount = len(shape.parts)
        print(partCount)
        # 处理除最后一个部分之外的其他部分
        for i in range(partCount-1):
            for j in range(shape.parts[i], shape.parts[i+1]-1):
                # print(shape.points)
                pX = Calculate_IJ(minX, shape.points[j][0], resolutionX)
                pY = Calculate_IJ(maxY, shape.points[j][1], resolutionY)
                pixels.append((pX, pY))

    # for ishape in inShp.shapes():
    #     print(ishape.points)
    #     for p in ishape.points:
    #         pX = Calculate_IJ(minX, p[0], resolutionX)
    #         pY = Calculate_IJ(maxY, p[1], resolutionY)
    #         pixels.append((pX, pY))

    rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)
    rasterize = ImageDraw.Draw(rasterPoly)
    rasterize.polygon(pixels, 0)
    mask = ImageToArray(rasterPoly)

    # Clip the image using the mask
    # clip = gdalnumeric.choose(mask, \
    #     (clip, 0)).astype(np.float)
    # clip = clip.astype(np.float)
    # clip[clip > 1] = 0

    clip = gdalnumeric.choose(mask, (clip, 0))
    # clip = clip.astype(gdalnumeric.uint8)
    # clip[clip == 0] = np.nan
    # clip[clip >  1] = np.nan

    # WriteTiff("./DATA/clip1.tif", clip, geoTrans, proj)
    # WriteHDF("clip.HDF", 'clip', clip, 1)
    # WriteHDF("clip.HDF", 'mask', mask, 0)
    # WriteHDF("clip.HDF", 'pixels', pixels, 0)

    return clip

# if __name__ == '__main__':
#     #shapefile_path, raster_path
#     # shapefile_path = './DATA/hancock/hancock.shp'
#     # raster_path = './DATA/FalseColor.tif'
#     # shapefile_path = r'E:\Personal\kangning\CODE\source\china_province_polygon.shp'
#     shapefile_path =  r'E:\Personal\kangning\CODE\source\china_boundary_polygon.shp'
#     filename = r'E:\Personal\kangning\LMI_20190507\MON-NC\FY4A-_LMI---_N_REGX_1047E_L3-_LIDS_SING_NUL_20170801000000_20170831235959_7800M_AMV01.NC'
#     # raster_path = './DATA/MODND1D.20160517.CN.NDVI.V2.TIF'
#
#     main( shapefile_path, filename )








