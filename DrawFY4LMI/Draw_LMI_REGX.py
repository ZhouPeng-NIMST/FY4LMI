#coding:utf-8

import netCDF4
import h5py
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.basemap import Basemap
import os
import sys
import numpy as np
import matplotlib.colors as colors
import re
import datetime
exepath = os.path.dirname(__file__)
sys.path.append(exepath)
sys.path.append(os.path.join(exepath, '..'))

from NCProcess import ReadNC
from ShapeClipRaster import *
from  HDFProcess import ReadHDF
from config import *


def DrawALLImage(outname, data, lat, lon, left_lon=-180.0, right_lon=180.0, top_lat=90.0, buttom_lat=-90.0):
    '''
    绘制全区域图像
    :param outname: 输出图像名
    :param data: 输入闪电密度数据
    :param lat: 纬度
    :param lon: 经度
    :return:
    '''
    data = data[::-1,:]
    lat[lat>90] = np.nan
    lat[lat<-90] = np.nan

    lon[lon>180] = np.nan
    lon[lon<-180] = np.nan
    data[data==0] = np.nan
    max_lat = np.nanmax(lat)
    min_lat = np.nanmin(lat)
    max_lon = np.nanmax(lon)
    min_lon = np.nanmin(lon)

    max_lat = np.ceil(max_lat / 10.0) * 10.0
    min_lat = np.floor(min_lat / 10.0) * 10.0
    max_lon = np.ceil(max_lon / 10.0) * 10.0
    min_lon = np.floor(min_lon / 10.0) * 10.0

    max_data = np.nanmax(data)
    min_data = np.nanmin(data)

    print(max_lon,max_lat)
    print(min_lon, min_lat)
    fig=plt.figure(figsize=(11, 6))
    ax = fig.add_axes([.0, .1, 1.0, .8])

    m = Basemap(projection='cyl', llcrnrlat=min_lat, urcrnrlat=max_lat, llcrnrlon=min_lon, urcrnrlon=max_lon, resolution='c',)
    # m = Basemap(projection='cyl', llcrnrlat=m_box[1], urcrnrlat=m_box[3], llcrnrlon=m_box[0], urcrnrlon=m_box[2], resolution='c',)

    m.drawparallels(np.arange(min_lat, max_lat, 5.0),
                    color='k',
                    labels=[1, 1, 0, 0],
                    # dashes=[1, 1],
                    linewidth=0.2)
    m.drawmeridians(np.arange(min_lon, max_lon, 5.0),
                        color='k',
                        labels=[0, 0, 1, 0],
                        # fmt=lon_fmt,
                        # dashes=[1, 1],
                        linewidth=0.2)
    # cmap, norm, bounds = ColorBar()
    norm = colors.Normalize(vmin=min_data, vmax=max_data)
    cmap = matplotlib.cm.jet

    sc = m.imshow(data, norm = norm, cmap=matplotlib.cm.jet, interpolation = 'nearest')
    # m.scatter(lon, lat, data, norm = norm, cmap=cmap,marker='o')
    # m.scatter(lon, lat, c = data,cmap=matplotlib.cm.jet, marker='.',s = 5)
    m.readshapefile(os.path.join(os.path.dirname(__file__),'..','source','china_province_polygon'),
                    'counties',
                    drawbounds=True,
                    linewidth=1,
                    color='k'
                    )
    m.readshapefile(os.path.join(os.path.dirname(__file__),'..','source','global_country_boundary'),
                    'counties',
                    drawbounds=True,
                    linewidth=0.5,
                    color='k'
                    )
    # 画图例
    ax = fig.add_axes([0.25, 0.06, 0.5, .03])
    cb3 = matplotlib.colorbar.ColorbarBase(ax, cmap=cmap,
                                    norm=norm,
                                    # boundaries=[-10] + bounds + [10],
                                    # extend='both',    # max, min, both
                                    # Make the length of each extension
                                    # the same as the length of the
                                    # interior colors:
                                    # extendfrac='auto',
                                    # ticks=bounds,
                                    spacing='uniform',
                                    orientation='horizontal')
    # cb3.set_ticklabels(map(str,bounds))
    # cb3.set_label('flashes/km^2/year')
    #bounds = [0.0, 0.1, 0.2, 0.4, 0.6, 0.8, 1, 2, 4, 6, 8, 10, 15, 20, 30, 40, 50, 70]
    # plt.show()
    plt.savefig(outname, dpi= 200, bbox_to_anchor = 'tight')
    print('%s output success!!!' %outname)


def DrawChinaImage(outname, data, lat, lon, left_lon=70.0, right_lon=140.0, top_lat=60.0, buttom_lat=0.0):
    '''
    绘制中国区域图像,其中将南海区域绘制成子图
    :param outname: 输出图像名
    :param data: 输入闪电密度数据
    :param lat: 纬度
    :param lon: 经度
    :return:
    '''
    # data = srcdata[::-1,:]
    lat[lat>90] = np.nan
    lat[lat<-90] = np.nan

    lon[lon>180] = np.nan
    lon[lon<-180] = np.nan
    data[data==0] = np.nan
    max_data_lat = np.nanmax(lat)
    min_data_lat = np.nanmin(lat)
    max_data_lon = np.nanmax(lon)
    min_data_lon = np.nanmin(lon)
    max_data_data = np.nanmax(data)
    min_data_data = np.nanmin(data)

    # 中国区域范围
    max_lat = China_Max_Lat
    min_lat = China_Min_Lat
    max_lon = China_Max_Lon
    min_lon = China_Min_Lon

    # 裁剪中国区域范围内的数据
    if max_lat > max_data_lat:
        max_lat = max_data_lat

    if min_lat < min_data_lat:
        min_lat = min_data_lat

    if max_lon > max_data_lon:
        max_lon = max_data_lon

    if min_lon < min_data_lon:
        min_lon = min_data_lon

    max_lat = np.ceil(max_lat / 10.0) * 10.0
    min_lat = np.floor(min_lat / 10.0) * 10.0
    max_lon = np.ceil(max_lon / 10.0) * 10.0
    min_lon = np.floor(min_lon / 10.0) * 10.0

    # 从全圆盘数据中裁剪中国区域数据
    s_row = int(np.round(np.fabs(max_data_lat - max_lat) / glb_Y_Resolution))
    e_row = int(np.round(np.fabs(min_data_lat - max_lat) / glb_Y_Resolution))

    s_col = int(np.round(np.fabs(min_lon - min_data_lon) / glb_X_Resolution))
    e_col = int(np.round(np.fabs(max_lon - min_data_lon) / glb_X_Resolution))

    print(s_row,e_row, s_col,e_col)

    data = data[s_row:e_row, s_col:e_col]
    data = data[::-1,:]
    max_data = np.nanmax(data)
    min_data = np.nanmin(data)

    print(max_lon,max_lat)
    print(min_lon, min_lat)

    # 开始绘图...
    fig=plt.figure(figsize=(10, 8))
    ax = fig.add_axes([.0, .1, 1.0, .8])

    m = Basemap(projection='cyl', llcrnrlat=min_lat, urcrnrlat=max_lat, llcrnrlon=min_lon, urcrnrlon=max_lon, resolution='c',)
    # m = Basemap(projection='cyl', llcrnrlat=m_box[1], urcrnrlat=m_box[3], llcrnrlon=m_box[0], urcrnrlon=m_box[2], resolution='c',)

    m.drawparallels(np.arange(min_lat, max_lat, 5),
                    color='k',
                    labels=[1, 1, 0, 0],
                    # dashes=[1, 1],
                    linewidth=0.2)
    m.drawmeridians(np.arange(min_lon, max_lon, 5),
                        color='k',
                        labels=[0, 0, 1, 0],
                        # fmt=lon_fmt,
                        # dashes=[1, 1],
                        linewidth=0.2)
    # cmap, norm, bounds = ColorBar()
    norm = colors.Normalize(vmin=min_data, vmax=max_data)
    cmap = matplotlib.cm.jet

    sc = m.imshow(data, norm = norm, cmap=matplotlib.cm.jet, interpolation = 'nearest')
    # m.scatter(lon, lat, data, norm = norm, cmap=cmap,marker='o')
    # m.scatter(lon, lat, c = data,cmap=matplotlib.cm.jet, marker='.',s = 5)
    m.readshapefile(os.path.join(os.path.dirname(__file__),'..','source','china_province_polygon'),
                    'states',
                    drawbounds=True,
                    linewidth=1,
                    color='k'
                    )

    m.readshapefile(os.path.join(os.path.dirname(__file__),'..','source','global_country_boundary'),
                    'states',
                    drawbounds=True,
                    linewidth=0.5,
                    color='k'
                    )

    # 画图例
    ax = fig.add_axes([0.25, 0.06, 0.5, .03])
    cb3 = matplotlib.colorbar.ColorbarBase(ax, cmap=cmap,
                                    norm=norm,
                                    # boundaries=[-10] + bounds + [10],
                                    # extend='both',    # max, min, both
                                    # Make the length of each extension
                                    # the same as the length of the
                                    # interior colors:
                                    # extendfrac='auto',
                                    # ticks=bounds,

                                    spacing='uniform',
                                    orientation='horizontal')
    # cb3.set_ticklabels(map(str,bounds))
    # cb3.set_label('flashes/km^2/year')
    #bounds = [0.0, 0.1, 0.2, 0.4, 0.6, 0.8, 1, 2, 4, 6, 8, 10, 15, 20, 30, 40, 50, 70]
    # plt.show()
    plt.savefig(outname, dpi=200, bbox_to_anchor='tight')
    print('%s output success!!!' %outname)


def ColorBar():
    colorlist = [
        [168,168,168],
        [128,32,136],
        [168,24,176],
        [240,152,240],
        [0,0,144],
        [104,104,200],
        [200,200,224],
        [32,160,32],
        [112,208,112],
        [176,240,176],
        [224,224,0],
        [232,144,8],
        [200,128,32],
        [192,112,48],
        [208,0,0],
        [160,0,0],
        [56,56,56],
    ]

    clor = ["#%02x%02x%02x" %(i[0], i[1], i[2]) for i in colorlist]
    print(clor)


    # cmap = matplotlib.colors.ListedColormap([[0., .4, 1.], [0., .8, 1.],[1., .8, 0.], [1., .4, 0.]])
    cmap = matplotlib.colors.ListedColormap(clor, 'indexed')
    # cmap.set_over((1., 0., 0.))
    # cmap.set_under((0., 0., 1.))

    # bounds = [-1., -.5, 0., .5, 1.]
    bounds = [0.0, 0.1, 0.2, 0.4, 0.6, 0.8, 1, 2, 4, 6, 8, 10, 15, 20, 30, 40, 50, 70]
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

    return cmap, norm, bounds


def WriteTXT(filename, data, overwrite=1):
    '''
    输出统计数据文本文件
    :param filename: 输出文件名
    :param data: 统计数据
    :param overwrite: 是否创建新文件， 1：创建，非1：增加输出
    :return:
    '''
    if overwrite == 1:
        fout = open(filename, 'w')
        # 增加写头
        fout.write('{0:15}{1:15}{2:15}{3:15}{4:15}{5:15}{6:15}{7:15}{8:15}{9:15}{10:15}{11:15}{12:15}'.format('StarDatetime', 'EndDatetime','Type',
                                                     'NOM_mean', 'NOM_max', 'NOM_min', 'NOM_std', 'NOM_pix',
                                                     'China_mean', 'China_max', 'China_min', 'China_std', 'China_pix'))
    else:
        fout = open(filename, 'a')
    fout.write('\n')
    fout.write('{0:15}{1:15}{2:<15}{3:<15.4f}{4:<15.4f}{5:<15.4f}{6:<15.4f}{7:<15.0f}{8:<15.4f}{9:<15.4f}{10:<15.4f}{11:<15.4f}{12:<15.0f}'.format(
            data[0],data[1], data[2], data[3], data[4],data[5], data[6], data[7], data[8], data[9],data[10], data[11],data[12]))

    fout.close()


def StatPix(data):
    flag = data <=0
    print(flag)
    return np.sum(flag)


def Draw_LMI_REGX(strdate, pathin=None, pathout=None, left_lon=-180, right_lon=180, top_lat=90, buttom_lat=-90):
    '''
    主程序接口，输入L3级合成文件，对合成文件进行统计并绘图
    :param strdate:
    :param pathin:
    :param pathout:
    :return:
    '''
    # 解析文件名
    # filename = r'../data/FY4A-_LMI---_N_REGX_1047E_L3-_LIDS_SING_NUL_20170801000000_20170831235959_7800M_AMV01.NC'
    # startime = datetime.datetime.strptime(strdate, '%Y%m%d%H%M%S')
    startime = strdate
    endtime = startime + datetime.timedelta(seconds=24*60*60-1)
    filename = os.path.join(pathin, 'FY4A-_LMI---_N_REGX_1047E_L3-_LIDS_SING_NUL_%s_%s_7800M_AMV01.NC'
                            %(startime.strftime('%Y%m%d%H%M%S'), endtime.strftime('%Y%m%d%H%M%S')))
    if not os.path.isfile(filename):
        print('%s is not exist, will be exit!!!' %filename)
        exit(1)

    # 解析文件名，提取文件名中的起始、结束时间以及合成类型（AM、AD、AY）
    name = os.path.basename(filename)
    namels = re.split('_',name)

    # 拼接输出统计文件TXT文件名
    outTXTname = os.path.join(pathout, '{}_{}_{}_{}_{}_{}_{}.TXT'.format(namels[0], namels[1],namels[5],namels[6],namels[9],namels[10], namels[12][0:2]))
    outPicName = outTXTname.replace('.TXT','.PNG')
    print(outTXTname)
    print(outPicName)

    Density = ReadNC(filename, 'Density')
    FLAT = ReadNC(filename, 'FLAT')
    FLON = ReadNC(filename, 'FLON')

    data = []

    # 从文件名中获取观测起始、结束时间，观测点ID，事件数量
    data.append(namels[9])
    data.append(namels[10])
    data.append(namels[12][0:2])

    NOM_max = np.nanmax(Density)
    NOM_min = np.nanmin(Density)
    NOM_mean=np.nanmean(Density)
    NOM_std = np.nanstd(Density)
    NOM_pix = np.count_nonzero(Density)

    data.append(NOM_mean)
    data.append(NOM_max)
    data.append(NOM_min)
    data.append(NOM_std)
    data.append(NOM_pix)

    # 开始绘图
    DrawALLImage(outPicName, Density, FLAT, FLON)
    DrawChinaImage(outPicName.replace('.PNG', '_CHINA.PNG'), Density, FLAT, FLON)

    Line = (60 - FLAT) / xresolut + 0.5
    Col = (FLON - 70) / yresolut + 0.5
    Line = np.array(Line, dtype=np.int32)
    Col = np.array(Col, dtype=np.int32)
    # 裁剪中国区域图像
    # clip = ShapeClipRaster(China_ShpFile, FLAT, FLON, Density)
    mask = ReadHDF(China_Mask_FileName, 'mask')
    flag = (Line >= 0) & (Line < mask.shape[0])
    Line = Line[flag]
    Col = Col[flag]
    Density = Density[flag]

    flag = (Col >= 0) & (Col < mask.shape[1])
    Line = Line[flag]
    Col = Col[flag]
    Density = Density[flag]

    mask = mask[Line, Col]
    Flag = mask==1
    clip = Density[Flag]

    # WriteHDF('./data/clip.HDF', 'clip', clip, 1)
    # 定义输出变量列表，将输出数据存入变量中

    if len(clip) <= 0 :
        China_pix = -999
        China_max = -999
        China_min = -999
        China_mean = -999
        China_std = -999
    else:
        China_pix = np.count_nonzero(clip)
        clip[clip==0] = np.nan
        clip[clip==65535.0] = np.nan
        China_max = np.nanmax(clip)
        China_min = np.nanmin(clip)
        China_mean = np.nanmean(clip)
        China_std = np.nanstd(clip)

    data.append(China_mean)
    data.append(China_max)
    data.append(China_min)
    data.append(China_std)
    data.append(China_pix)

    WriteTXT(outTXTname, data, 1)

def DrawREGNImage(strdate, WorkType = 1):
    '''

    :param strdate:
    :param WorkType:
    :return:
    '''
    if WorkType == 0 :
        return None
    dt = datetime.datetime.strptime(strdate, '%Y%m%d%H%M%S')
    # 拼接L3级 输入、输出目录
    # L3_density_pathin = os.path.join( PATH_L3_File, dt.strftime('%Y%m%d'))
    L3_density_pathin = PATH_L3_File

    # L3_density_pathout = os.path.join( PATH_OUT_Density, dt.strftime('%Y%m%d'))
    L3_density_pathout = PATH_OUT_Density
    if not os.path.isdir(L3_density_pathout):
        print('%s is not exist, will be created!!' % L3_density_pathout)
        os.makedirs(L3_density_pathout)

    # step4: 统计L3级文件，并绘制区域图像（日期匹配，定时调用）
    Draw_LMI_REGX(dt, L3_density_pathin, L3_density_pathout)


if __name__ == '__main__':

    Draw_LMI_REGX()