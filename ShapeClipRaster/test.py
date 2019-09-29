#coding:utf-8
'''
@author : @libin
@e_mail : libin033@163.com
@brief: 矢量数据裁剪栅格
'''

from osgeo import gdalnumeric, gdal_array
from PIL import Image, ImageDraw
import os
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


def ReadNC(filename, sdsname):
    if not os.path.isfile(filename):
        print('%s is not exist, will be exited!!!' %filename)
        exit(1)

    fin = netCDF4.Dataset(filename, 'r')
    data = fin.variables[sdsname][:]
    fin.close()

    return data

def ImageToArray(i):
    """
    Converts a Python Imaging Library array to a
    gdalnumeric image.
    """
    # a=gdalnumeric.fromstring(i.tobytes(),'b')
    a = gdal_array.numpy.fromstring(i.tobytes(),'b')
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


def ShapeClipRaster( shapefile_filename,  FLAT, FLON, srcArray, resolutionX=0.01, resolutionY=0.01):

    if not os.path.isfile(shapefile_filename):
        print("%s is not exist, will be exit!!!" %shapefile_filename)
        exit(3)
    inShp = shapefile.Reader(shapefile_filename)

    # 获取shapefile文件经纬度范围
    minX, minY, maxX, maxY = inShp.bbox
    print('minX, maxX, minY, maxY:',minX, maxX, minY, maxY)

    # 获取裁剪区域范围的经纬度
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

    xoffset =  ulX
    yoffset =  ulY
    print("Xoffset, Yoffset = ( %d, %d )" % ( xoffset, yoffset ))

    rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)
    rasterize = ImageDraw.Draw(rasterPoly)

    for shape in inShp.shapes():
        partCount = len(shape.parts)
        print(partCount)

        # 处理除最后一个部分之外的其他部分
        for i in range(partCount-1):
            pixels = []
            for j in range(shape.parts[i], shape.parts[i+1]-1):
                pX = Calculate_IJ(minX, shape.points[j][0], resolutionX)
                pY = Calculate_IJ(maxY, shape.points[j][1], resolutionY)
                pixels.append((pX, pY))
            rasterize.polygon(pixels, 0)

    mask = ImageToArray(rasterPoly)

    clip = gdalnumeric.choose(mask, (clip, 0))
    # clip = clip.astype(gdalnumeric.uint8)
    # clip[clip == 0] = np.nan
    # clip[clip >  1] = np.nan

    WriteHDF("clip.HDF", 'clip', clip, 1)
    WriteHDF("clip.HDF", 'mask', mask, 0)
    WriteHDF("clip.HDF", 'pixels', pixels, 0)

    return clip

def GetMask(shapefile_filename,  FLAT, FLON, resolutionX=0.01, resolutionY=0.01):

    if not os.path.isfile(shapefile_filename):
        print("%s not exist, will return!!!" %shapefile_filename)
        return []
    inShp = shapefile.Reader(shapefile_filename)

    # 获取shapefile文件经纬度范围
    minX, minY, maxX, maxY = inShp.bbox
    print('minX, maxX, minY, maxY:',minX, maxX, minY, maxY)

    # 获取裁剪区域范围的经纬度
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

    # 根据shapefile文件的范围对原始数据进行切片
    pxWidth = int(lrX - ulX)
    pxHeight = int(lrY - ulY)
    print(" pxHeight, pxWidth:", pxHeight, pxWidth)

    xoffset =  ulX
    yoffset =  ulY
    print("Xoffset, Yoffset = ( %d, %d )" % ( xoffset, yoffset ))

    rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)
    rasterize = ImageDraw.Draw(rasterPoly)

    for shape in inShp.shapes():
        partCount = len(shape.parts)
        print(partCount)

        # 处理除最后一个部分之外的其他部分
        for i in range(partCount-1):
            pixels = []
            for j in range(shape.parts[i], shape.parts[i+1]-1):
                pX = Calculate_IJ(minX, shape.points[j][0], resolutionX)
                pY = Calculate_IJ(maxY, shape.points[j][1], resolutionY)
                pixels.append((pX, pY))
            rasterize.polygon(pixels, 0)

    mask = ImageToArray(rasterPoly)

    return mask



def WriteHDF(filename, sdsname, data,overwrite = 1, dictfileattrs=None, dictdsetattrs = None, dictgrpattrs = None):
    '''
    mode
    r Readonly, file must exist
    r+ Read/write, file must exist
    w Create file, truncate if exists
    w- or x Create file, fail if exists
    a Read/write if exists, create otherwise (default)
    :param filename:
    :param sdsname:
    :param data:
    :param overwrite:
    :return:
    '''
    if overwrite == 1:
        fout = h5py.File(filename,'w')
    else:
        fout = h5py.File(filename, 'a')

    # fout[sdsname] = data

    dsetis = fout.create_dataset(sdsname,  data=data)
    fout.close()

if __name__ == '__main__':
#     #shapefile_path, raster_path
#     # shapefile_path = './DATA/hancock/hancock.shp'
#     # raster_path = './DATA/FalseColor.tif'
#     # shapefile_path = r'E:\Personal\kangning\CODE\source\china_province_polygon.shp'
    shapefile_path =  r'../source/china_boundary_polygon.shp'
    filename = r'../data/input/FY4A-_LMI---_N_REGX_1047E_L3-_LIDS_SING_NUL_20170801000000_20170831235959_7800M_AMV01.NC'
#     # raster_path = './DATA/MODND1D.20160517.CN.NDVI.V2.TIF'
#
    srcArray = ReadNC(filename, "Density")
    FLAT = ReadNC(filename, "FLAT")
    FLON = ReadNC(filename, "FLON")
    ShapeClipRaster( shapefile_path, FLAT, FLON, srcArray, 0.25, 0.25)








