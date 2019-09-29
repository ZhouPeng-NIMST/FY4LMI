#coding:utf-8
import netCDF4
import h5py
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import matplotlib
# from mpl_toolkits.basemap import Basemap
import os
import numpy as np
import gdal
import matplotlib.colors as colors

global m_box

def DrawShape():
    import shapefile

    shapename = r'../source/china_boundary_polygon.shp'

    r =shapefile.Reader(shapename)
    # 计算
    xdist = m_box[2] - m_box[0]
    ydist = m_box[3] - m_box[1]
    iwidth = 2400
    iheigh = 1600
    xratio = iwidth / xdist
    yratio = iheigh / ydist
    print(xratio, yratio)
    def LatLon2RowCol(lon, lat):
        px = int(iwidth - ((m_box[2] - lon) * xratio))
        py = int( (m_box[3] - lat) * yratio)
        return (px,py)

    OL_WIDTH = 1
    OL_COLOR = "rgb(0, 0, 0)"
    img = Image.new("RGB", (iwidth, iheigh), "white")
    draw = ImageDraw.Draw(img)
    shapes = r.shapes()
    for shape in shapes:
            partCount = len(shape.parts)
            print(partCount)
            # 处理除最后一个部分之外的其他部分
            for i in range(partCount-1):
                for j in range(shape.parts[i], shape.parts[i+1]-1):
                    # print(shape.points)
                    xy1 = LatLon2RowCol(shape.points[j][0], shape.points[j][1])
                    xy2 = LatLon2RowCol(shape.points[j+1][0], shape.points[j+1][1])
                    distance = np.sqrt((xy2[0] - xy1[0]) * (xy2[0] - xy1[0]) + (xy2[1] - xy1[1]) * (xy2[1] - xy1[1]))
                    if distance > 15:
                        print(xy1, xy2)
                        continue
                    if len(xy1) > 0 and len(xy2) > 0:
                        draw.line((xy1[0], xy1[1], xy2[0], xy2[1]), fill=(OL_COLOR), width=OL_WIDTH)

            # 处理最后一部分
            for j in range(shape.parts[-1], len(shape.points)-1):
                # print(shape.points[j])
                xy1 = LatLon2RowCol(shape.points[j][0], shape.points[j][1])
                xy2 = LatLon2RowCol(shape.points[j+1][0], shape.points[j+1][1])
                if len(xy1) > 0 and len(xy2) > 0:
                    draw.line((xy1[0], xy1[1], xy2[0], xy2[1]), fill=(OL_COLOR), width=OL_WIDTH)

            # 处理最后一个点
            xy1 = LatLon2RowCol(shape.points[-1][0], shape.points[-1][1])
            xy2 = LatLon2RowCol(shape.points[-2][0], shape.points[-2][1])
            if len(xy1) > 0 and len(xy2) > 0:
                draw.line((xy1[0], xy1[1], xy2[0], xy2[1]), fill=(OL_COLOR), width=OL_WIDTH)

    #draw.polygon(pixels, outline="rgb(0, 0, 0)", fill="rgb(198, 204,189)")
    img.save("test.png")




    # xdist = m_box[2] - m_box[0]
    # ydist = m_box[3] - m_box[1]
    # iwidth = 1200
    # iheigh = 800
    # xratio = iwidth / xdist
    # yratio = iheigh / ydist
    #
    #
    # c = pngcanvas.PNGCanvas(iwidth, iheigh)
    # f = open("china.png", 'wb')
    #
    # # pixels = []
    # # for x, y in r.shapes()[0].points:
    # #     px = int(iwidth - (m_box[2] - x) * xratio)
    # #     py = int((m_box[3] - y) * yratio)
    # #     pixels.append([px, py])
    # #     print(x, y)
    # # c.polyline(pixels)
    # # f.write(c.dump())
    #
    # for i in range(len(r.shapes())):
    #     pixels = []
    #     for x, y in r.shapes()[i].points:
    #         px = int(iwidth - (m_box[2] - x) * xratio)
    #         py = int((m_box[3] - y) * yratio)
    #         pixels.append([px, py])
    #         # print(x, y)
    #     c.polyline(pixels)
    #     f.write(c.dump())
    # f.close()



def ReadNC(filename, sdsname):
    if not os.path.isfile(filename):
        print("%s is not exist,will be return!!!" %filename)
        exit(1)

    fin = netCDF4.Dataset(filename, 'r')
    data = fin[sdsname][:]
    fin.close()

    return data

def ImshowDraw(data):
    print(np.nanmax(data))

    data[data<=0] = np.nan

    fig=plt.figure(figsize=(9, 8))
    ax = fig.add_axes([.0, .1, 1.0, .8])

    m = Basemap(projection='cyl', llcrnrlat=0, urcrnrlat=60, llcrnrlon=70, urcrnrlon=140, resolution='c',)
    # m = Basemap(projection='cyl', llcrnrlat=m_box[1], urcrnrlat=m_box[3], llcrnrlon=m_box[0], urcrnrlon=m_box[2], resolution='c',)

    m.drawparallels(range(0, 60, 5),
                    color='m',
                    labels=[1, 1, 0, 0],
                    # dashes=[1, 1],
                    linewidth=0.2)
    m.drawmeridians(range(70, 140, 5),
                        color='m',
                        labels=[0, 0, 1, 0],
                        # fmt=lon_fmt,
                        # dashes=[1, 1],
                        linewidth=0.2)

    norm = colors.Normalize(vmin=0, vmax=10)
    cmap = matplotlib.cm.jet
    # cmap = matplotlib.cm.rainbow
    cmap, norm, bounds = ColorBar()
    # sc = plt.imshow(data, norm = norm, cmap=cmap, interpolation = 'nearest')
    a1,b1 =data.shape
    t=int(a1/180.*(90-  60))
    b=int(a1/180.*(90-  0))
    l=int(b1/360.*(180+ 70))
    r=int(b1/360.*(180+140))
    print(t,b,l,r,a1,b1)
    data1=data[b:t:-1,l:r]
    print( data1.shape)

    sc = m.imshow(data1, norm = norm, cmap=cmap, interpolation = 'nearest')
    # m.readshapefile(r'../DATA/boundary', 'states',drawbounds=True)
    m.readshapefile(r'E:\GlobalData\china\polygon\china_province_polygon', 'states',drawbounds=True)
    # m.readshapefile(u'E:\Personal\kangning\全国各省市三级的行政图和南海诸岛的shp\China\CHN_adm1', 'states',drawbounds=True)
    # m.readshapefile(u'E:\Personal\kangning\全国各省市三级的行政图和南海诸岛的shp\China\南海诸岛及其它岛屿', 'states',drawbounds=True)

    #加colorbar及colorbar的刻度
    # cb = plt.colorbar(sc, orientation='horizontal')

    # 画子图
    W = 4
    ax = fig.add_axes([(24-W-2.05)/24., .1, W/24., 26./(125-103)*W/21.4])
    m = Basemap(projection='cyl', llcrnrlat=0, urcrnrlat=26, llcrnrlon=103, urcrnrlon=125, resolution='c',)
    # m = Basemap(projection='cyl', llcrnrlat=m_box[1], urcrnrlat=m_box[3], llcrnrlon=m_box[0], urcrnrlon=m_box[2], resolution='c',)
    norm = colors.Normalize(vmin=0, vmax=10)
    cmap = matplotlib.cm.jet
    # cmap = matplotlib.cm.rainbow
    cmap, norm, bounds = ColorBar()
    # sc = plt.imshow(data, norm = norm, cmap=cmap, interpolation = 'nearest')
    a1,b1 =data.shape
    t=int(a1/180.*(90-  26))
    b=int(a1/180.*(90-  0))
    l=int(b1/360.*(180+ 103))
    r=int(b1/360.*(180+125))
    print(t,b,l,r,a1,b1)
    data1=data[b:t:-1,l:r]
    print( data1.shape)

    sc = m.imshow(data1, norm = norm, cmap=cmap, interpolation = 'nearest')
    m.readshapefile(r'E:\GlobalData\china\polygon\china_province_polygon', 'states',drawbounds=True)
    # m.readshapefile(u'E:\Personal\kangning\全国各省市三级的行政图和南海诸岛的shp\China\CHN_adm1', 'states',drawbounds=True)
    # m.readshapefile(u'E:\Personal\kangning\全国各省市三级的行政图和南海诸岛的shp\China\南海诸岛及其它岛屿', 'states',drawbounds=True)

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
    #bounds = [0.0, 0.1, 0.2, 0.4, 0.6, 0.8, 1, 2, 4, 6, 8, 10, 15, 20, 30, 40, 50, 70]
    # plt.show()
    plt.savefig("chinaaa.png", bbox_to_anchor = 'tight')

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
    fig=plt.figure(figsize=(14 , 8 ))
    ax = fig.add_axes([.05, .05, 0.9, .07])
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
    # cb3.set_label('Custom extension lengths, some other units')
    plt.show()

def BaseDraw(lat, lon, data):
    fig=plt.figure(figsize=(14 , 8 ))
    ax = fig.add_axes([.05, .05, 0.8, .80])
    # m = Basemap(projection='cyl', llcrnrlat=35, urcrnrlat=55, llcrnrlon=96, urcrnrlon=128, resolution='c',)
    m = Basemap(projection='cyl', llcrnrlat=0, urcrnrlat=60, llcrnrlon=70, urcrnrlon=140, resolution='c',)

    m.drawparallels(range(0, 55, 5), color='black', dashes=[1, 1], linewidth=0.2)
    m.drawmeridians(range(70, 140, 15), color='black', dashes=[1, 1], linewidth=0.2)
    # m.drawparallels(range(-90, 90, 10), color='m', labels=[1, 0, 0, 0],
    #                     dashes=[1, 1], linewidth=0.2)
    # m.drawmeridians(range(-180, 180, 10),
    #                     color='m',
    #                     labels=[0, 0, 0, 1],
    #                     fmt=lon_fmt,
    #                     dashes=[1, 1],
    #                     linewidth=0.2)

    # m.drawcoastlines(linewidth=0.5, linestyle='solid', color=(0, 0, 0, 0.8))
    # m.drawcountries(linewidth=0.2, linestyle='solid', color=(0, 0, 0, 1))
    m.ax = ax
    m.readshapefile(r'E:\GlobalData\china\polygon\china_province_polygon', 'states',drawbounds=True)
    # #画底图上的经纬度网格
    # m.drawparallels(np.arange(minlat, maxlat+5, 5), color='w', labels=[1, 0, 0, 0],
    #                 dashes=[1, 1], linewidth=0.2,fontsize=20)
    # m.drawmeridians(np.arange(minlon, maxlon+2.5, 2.5), color='w', labels=[0, 0, 0, 1],
    #                 dashes=[1, 1], linewidth=0.2,fontsize=20)
    #在底图上画点

    # sc = m.scatter(lon, lat, c=data, cmap=matplotlib.cm.jet, marker='.',s = 5)
    sc = m.scatter(lon, lat, c=data, cmap=matplotlib.cm.jet, marker='s',s = 10)
    #sc = m.scatter(lon0, lat0,  cmap=matplotlib.cm.jet, marker='o', s=20)

    #加colorbar及colorbar的刻度
    cb = plt.colorbar(sc, fraction=0.046, pad=0.02, orientation='horizontal')
    # cb.set_label('$BT(K)$', size=20)
    # cb.ax.tick_params(labelsize = 20)
    #保存图片
    plt.show()
    #plt.savefig(outname, dpi=dpi, bbox_inches='tight')

def write_img(filename,im_proj,im_geotrans,im_data):
        '''
        写GeoTIF文件
        :param filename:输出文件名
        :param im_proj: 投影信息
        :param im_geotrans: 仿射变换
        :param im_data: 输入数据
        :return:
        '''
        #gdal数据类型包括
        #gdal.GDT_Byte,
        #gdal .GDT_UInt16, gdal.GDT_Int16, gdal.GDT_UInt32, gdal.GDT_Int32,
        #gdal.GDT_Float32, gdal.GDT_Float64

        #判断栅格数据的数据类型
        # if 'int8' in im_data.dtype.name:
        #     datatype = gdal.GDT_Byte
        # elif 'int16' in im_data.dtype.name:
        #     datatype = gdal.GDT_UInt16
        # else:
        #     datatype = gdal.GDT_Float32

        isize = im_data.shape
        im_width = isize[1]
        im_height = isize[0]
        im_bands = 1

        #判读数组维数
        # if len(im_data.shape) == 3:
        #     im_bands, im_height, im_width = im_data.shape
        # else:
        #     im_bands, (im_height, im_width) = 1,im_data.shape

        #创建文件
        driver = gdal.GetDriverByName("GTiff")            #数据类型必须有，因为要计算需要多大内存空间
        dataset = driver.Create(filename, im_width, im_height, 1, gdal.GDT_Float32)

        dataset.SetGeoTransform(im_geotrans)              #写入仿射变换参数
        dataset.SetProjection(im_proj)                    #写入投影

        if im_bands == 1:
            dataset.GetRasterBand(1).WriteArray(im_data)  #写入数组数据
        else:
            for i in range(im_bands):
                dataset.GetRasterBand(i+1).WriteArray(im_data[i])

        del dataset





if __name__ == '__main__':
    m_box = [70,  0, 140, 60]
    DrawShape()
    exit(1)
    # filaneme = r'../DATA/LISOTD_HRFC_V2.3.2015.nc'
    filaneme1 = r'../DATA/VHRFC_GLL.HDF'
    filaneme2 = r'../DATA/GLL.HDF'
    # filaneme = r'../DATA/lis_vhrfc_1998_2013_v01.nc/VHRFC.nc'



    VHRFC_LIS_FRD = ReadNC(filaneme1, 'HRFC_LIS_RF')
    HRFC_LIS_RF = ReadNC(filaneme2, 'HRFC_LIS_RF')
    VHRFC_LIS_FRD[:509] = HRFC_LIS_RF[:509]
    # VHRFC_LIS_FRD = ReadNC(filaneme, 'HRFC_LIS_RF')
    # lon, lat = np.meshgrid(Longitude, Latitude)
    # BaseDraw(Latitude, Longitude, HRFC_LIS_RF)
    # ImshowDraw(HRFC_LIS_RF)
    ImshowDraw(VHRFC_LIS_FRD)
    # ColorBar()
    exit(0)

    proj = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],' \
    'AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]'
    geotrans = [lon[0][0], 0.5, 0.0, lat[0][0], 0, 0.5]
    write_img('test.tiff',proj,geotrans,HRFC_LIS_RF) #写数据