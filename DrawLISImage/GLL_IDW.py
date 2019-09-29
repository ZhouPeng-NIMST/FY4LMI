#coding:utf-8
import netCDF4
import h5py
import os
from ctypes import *
import numpy.ctypeslib as npct
import numpy as np
import sys
from netCDF4 import Dataset

# sys.path.append('../Draw_Prof_Image/')
# from Draw_Prof import *


# 定义python调用C++的数据类型
array_1d_ushort= npct.ndpointer(dtype=np.uint16, ndim=1, flags='CONTIGUOUS')
array_1d_short= npct.ndpointer(dtype=np.int16, ndim=1, flags='CONTIGUOUS')
array_1d_int= npct.ndpointer(dtype=np.int32, ndim=1, flags='CONTIGUOUS')
array_1d_long= npct.ndpointer(dtype=np.long, ndim=1, flags='CONTIGUOUS')

array_1d_float = npct.ndpointer(dtype=np.float32, ndim=1, flags='CONTIGUOUS')
array_1d_double = npct.ndpointer(dtype=np.double, ndim=1, flags='CONTIGUOUS')


array_2d_short= npct.ndpointer(dtype=np.int16, ndim=2, flags='CONTIGUOUS')
array_2d_int= npct.ndpointer(dtype=np.int32, ndim=2, flags='CONTIGUOUS')
array_2d_long= npct.ndpointer(dtype=np.long, ndim=2, flags='CONTIGUOUS')

array_2d_float= npct.ndpointer(dtype=np.float32, ndim=2, flags='CONTIGUOUS')
array_2d_double = npct.ndpointer(dtype=np.double, ndim=2, flags='CONTIGUOUS')

exefile = os.path.dirname(__file__)
dllname = os.path.join(exefile, 'lib','GLLPro.dll')
print dllname
# mylib = cdll.LoadLibrary(dllname)
mylib = cdll.LoadLibrary(r"G:\ProductAnalysis\C++\GIIRS_GLL\x64\Release\GLLPro.dll")
# mylib = cdll.LoadLibrary(r"G:\ProductAnalysis\C++\GIIRS_GLL\x64\Release\GLLPro.dll")

def PreData(Data_Lat, Data_Lon, srcData, fillvalue = -999999.0):

    LatResolu = 0.1
    LonResolu = 0.1

    Data_Lon = np.array(Data_Lon,dtype=np.float32)
    Data_Lat = np.array(Data_Lat,dtype=np.float32)
    srcData = np.array(srcData,dtype=np.float32)

    srcHeight = srcData.shape[0]
    srcWidth = srcData.shape[1]
    print srcHeight, srcWidth
    # 加载静态库
    #mylib = cdll.LoadLibrary(r"G:\ProductAnalysis\C++\GLLPro\x64\Release\GLLPro.dll")

    # 获取区域范围
    # fExtend = np.full((4),fillvalue, dtype=np.float32)
    fExtend = [90.0, -180.0, -90.0, 180.0]

    print 'fExtend:', fExtend
    outHight = int((fExtend[0] - fExtend[2]) / LatResolu + 0.5);
    outWidth = int((fExtend[3] - fExtend[1]) / LonResolu + 0.5);
    print outHight,outWidth

    # 做等经纬投影
    Data_GLL = np.full((outHight, outWidth), fillvalue, dtype=np.float32)
    mylib.GLL.restype = c_int
    mylib.GLL.argtypes = [array_2d_float, array_2d_float, array_2d_float, array_2d_float, c_int, c_int, c_int, c_int, c_float, c_float, c_float]
    mylib.GLL(Data_GLL, Data_Lat, Data_Lon, srcData, srcHeight, srcWidth, outHight, outWidth, LonResolu, LatResolu, fillvalue)
    # return Data_GLL

    # 做反距离插值
    Data_IDW = np.full((outHight, outWidth), fillvalue, dtype=np.float32)
    mylib.IDW.restype = c_int
    mylib.IDW.argtypes = [array_2d_float, array_2d_float, c_int, c_int, c_int,  c_float]
    mylib.IDW(Data_IDW, Data_GLL, outHight, outWidth, 25, fillvalue)
    # return Data_IDW

    # 做均值平滑
    Data_Smooth = np.full((outHight, outWidth), fillvalue, dtype=np.float32)
    mylib.Smooth.restype = c_int
    mylib.Smooth.argtypes = [array_2d_float, array_2d_float, c_int, c_int, c_int,  c_float]
    mylib.Smooth(Data_Smooth, Data_IDW, outHight, outWidth, 2, fillvalue)

    return  Data_Smooth

def ReadNC(filename, sdsname):
    if not os.path.isfile(filename):
        print("%s is not exist,will be return!!!" %filename)
        exit(1)

    fin = netCDF4.Dataset(filename, 'r')
    data = fin[sdsname][:]
    fin.close()

    return data

def WriteHDF(filename, sdsname, data, overwrite = 1):
    '''
    mode
            r        Readonly, file must exist
            r+       Read/write, file must exist
            w        Create file, truncate if exists
            w- or x  Create file, fail if exists
            a        Read/write if exists, create otherwise (default)
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

    fout[sdsname] = data

    fout.close()

if __name__ == '__main__':
    # filename = r'../DATA/LISOTD_HRFC_V2.3.2015.nc'
    #
    # HRFC_LIS_RF = ReadNC(filename, 'HRFC_COM_FR')
    # Latitude = ReadNC(filename, 'Latitude')
    # Longitude = ReadNC(filename, 'Longitude')

    filename = r'../DATA/lis_vhrfc_1998_2013_v01.nc/VHRFC.nc'
    VHRFC_LIS_FRD = ReadNC(filename, 'VHRFC_LIS_FRD')
    Latitude = ReadNC(filename, 'Latitude')
    Longitude = ReadNC(filename, 'Longitude')

    lon, lat = np.meshgrid(Longitude, Latitude)

    Data_IDW = PreData(lat, lon, VHRFC_LIS_FRD, 0.0)

    # Lat = np.arange(90, -90, -0.1)
    # Lon = np.arange(-180, 180, 0.1)
    # lon, lat = np.meshgrid(Lon, Lat)
    WriteHDF(r'../DATA/VHRFC_GLL.HDF', 'HRFC_LIS_RF', Data_IDW, 1)
    WriteHDF(r'../DATA/VHRFC_GLL.HDF', 'Longitude', lon, 0)
    WriteHDF(r'../DATA/VHRFC_GLL.HDF', 'Latitude', lat, 0)
    print lon




