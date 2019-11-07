#coding:utf-8
''''

'''
import os
import sys
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.colors as colors

exepath = os.path.dirname(__file__)
sys.path.append(os.path.join(exepath, '..'))
sys.path.append(os.path.join(exepath, '../..'))

from config import *

def DrawChineRegion(data, outname=None, left_lon=180, right_lon=180, top_lat=90, buttom_lat=-90):
    '''
    绘制中国区域专题图，并将南海区域单独绘制子图
    :param data: 输入数据，经过等经纬投影后的数据
    :param outname: 输出文件名
    :param left_lon:
    :param right_lon:
    :param top_lat:
    :param buttom_lat:
    :return:
    '''
    data[data<=0] = np.nan

    fig=plt.figure(figsize=(9, 8))
    ax = fig.add_axes([.0, .1, 1.0, .8])

    m = Basemap(projection='cyl', llcrnrlat=buttom_lat, urcrnrlat=top_lat, llcrnrlon=left_lon, urcrnrlon=right_lon, resolution='c',)
    # m = Basemap(projection='cyl', llcrnrlat=m_box[1], urcrnrlat=m_box[3], llcrnrlon=m_box[0], urcrnrlon=m_box[2], resolution='c',)

    m.drawparallels(range(buttom_lat, top_lat, 5),
                    color='m',
                    labels=[1, 1, 0, 0],
                    # dashes=[1, 1],
                    linewidth=0.2)
    m.drawmeridians(range(left_lon, right_lon, 5),
                        color='m',
                        labels=[0, 0, 1, 0],
                        # fmt=lon_fmt,
                        # dashes=[1, 1],
                        linewidth=0.2)

    # norm = colors.Normalize(vmin=0, vmax=10)
    # cmap = matplotlib.cm.jet
    # cmap = matplotlib.cm.rainbow
    cmap, norm, bounds = ColorBar()
    # sc = plt.imshow(data, norm = norm, cmap=cmap, interpolation = 'nearest')
    a1,b1 =data.shape
    t=int(a1/180.*(90 -  top_lat))
    b=int(a1/180.*(90 -  buttom_lat))
    l=int(b1/360.*(180 + left_lon))
    r=int(b1/360.*(180 + right_lon))
    # print(t,b,l,r,a1,b1)
    data1=data[b:t:-1,l:r]
    # print( data1.shape)

    sc = m.imshow(data1, norm = norm, cmap=cmap, interpolation = 'nearest')
    m.readshapefile(China_Province_Polygon, 'states', drawbounds=True)

    #加colorbar及colorbar的刻度
    # cb = plt.colorbar(sc, orientation='horizontal')

    # 画子图（南海区域）
    W = 4
    ax = fig.add_axes([(24-W-2.05)/24., .1, W/24., 26./(125-103)*W/21.4])
    m = Basemap(projection='cyl', llcrnrlat=0, urcrnrlat=26, llcrnrlon=103, urcrnrlon=125, resolution='c',)
    # m = Basemap(projection='cyl', llcrnrlat=m_box[1], urcrnrlat=m_box[3], llcrnrlon=m_box[0], urcrnrlon=m_box[2], resolution='c',)
    # norm = colors.Normalize(vmin=0, vmax=10)
    # cmap = matplotlib.cm.jet
    # cmap = matplotlib.cm.rainbow
    cmap, norm, bounds = ColorBar()
    # sc = plt.imshow(data, norm = norm, cmap=cmap, interpolation = 'nearest')
    a1,b1 = data.shape
    t=int(a1/180.*(90-  26))
    b=int(a1/180.*(90-  0))
    l=int(b1/360.*(180+ 103))
    r=int(b1/360.*(180+125))
    data1=data[b:t:-1,l:r]

    sc = m.imshow(data1, norm = norm, cmap=cmap, interpolation = 'nearest')
    m.readshapefile(China_Province_Polygon, 'states',drawbounds=True)

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
                                    ticks=bounds,
                                    spacing='uniform',
                                    orientation='horizontal')
    cb3.set_ticklabels(map(str,bounds))
    cb3.set_label('flashes/km^2/year')

    plt.savefig(outname, bbox_to_anchor = 'tight', dpi=200)

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
    # print(clor)


    # cmap = matplotlib.colors.ListedColormap([[0., .4, 1.], [0., .8, 1.],[1., .8, 0.], [1., .4, 0.]])
    cmap = matplotlib.colors.ListedColormap(clor, 'indexed')
    # cmap.set_over((1., 0., 0.))
    # cmap.set_under((0., 0., 1.))

    # bounds = [-1., -.5, 0., .5, 1.]
    bounds = [0.0, 0.1, 0.2, 0.4, 0.6, 0.8, 1, 2, 4, 6, 8, 10, 15, 20, 30, 40, 50, 70]
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

    return cmap, norm, bounds




