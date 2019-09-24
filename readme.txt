各个模块处理流程导向图



时间序列图 ======》  1min统计数据 ----> 进行日合成，输出日合成文件  -----> 绘制时间序列图
                        |
                        |
                        V
                     按天输出统计数据文件



密度分布图 =====》 全区域分布图 -----> 绘制全区域观测数据分布图  -----> 输出全区域数据统计文件
                        |
                        |
                        V
                    中国区域分布图(观测北半球时才绘制该图) -----> 输出中国区域数据统计文件
                    （Lon:70~140E, Lat:0~60N）


按天定时处理数据，对于闪电密度分布图，则按照L3文件合成日期推迟一天处理

目录结构：

data
    |--> 1min    -->  YYYY --> YYYYMMDD  -->  FY4A-_LMI---_L2-_LMIE_YYYYMMDD.TXT
                                         -->  FY4A-_LMI---_L2-_LMIE_YYYYMMDD_TimeList.TXT
                                         -->  FY4A-_LMI---_L2-_LMIE_YYYYMMDD_TimeList.PNG

    |-->Density  |-->  YYYY     -->  FY4A-_LMI---_L3-_LIDS_YYYYMMDDHHMMSS_yyyymmddhhmmss_AM.TXT
                                         -->  FY4A-_LMI---_L3-_LIDS_YYYYMMDDHHMMSS_yyyymmddhhmmss_AM.PNG
                                         -->  FY4A-_LMI---_L3-_LIDS_YYYYMMDDHHMMSS_yyyymmddhhmmss_AM_CHINA.PNG

                                         -->  FY4A-_LMI---_L3-_LIDS_YYYYMMDDHHMMSS_yyyymmddhhmmss_AY.TXT
                                         -->  FY4A-_LMI---_L3-_LIDS_YYYYMMDDHHMMSS_yyyymmddhhmmss_AY.PNG
                                         -->  FY4A-_LMI---_L3-_LIDS_YYYYMMDDHHMMSS_yyyymmddhhmmss_AY_CHINA.PNG


代码目录及功能结构：

DrawFY4LMI
          |-->  CombFile.py   --> CombFile(fils, outname):合成所有天数据文件，形成一个长时间序列数据文件
                                                           NowTime        StarDatetime   EndDatetime    Num            Events

          |-->  Draw_LMI_REGX.py  --> Draw_LMI_REGX(): 获取L3级产品文件密度数据，绘制全区域合成分布图和中国区域合成分布图
                                                        其中，中国区域合成分布图只观测北半球时绘制，并输出统计文件
                                                        StarDatetime   EndDatetime    Type
                                                        NOM_mean       NOM_max        NOM_min        NOM_std        NOM_pix
                                                        China_mean     China_max      China_min      China_std      China_pix

          |-->  DrawTimeList.py  -->  DrawTimeList() : 从长时间序列文件（HDF）中获取相关的时间数据和Event值，绘制相应的时间序列图

          |-->  Stat1MinData.py  -->  StatFile(strdate, pathin=None, flag = 1) : 统计 1min 观测数据的事件数，
                                                        并输出观测时间、任务起始、结束时间、探元编号、事件数
                                                        NowTime        StarDatetime   EndDatetime    Num            Events

ShapeClipRaster
          |-->  ShapeClipRaster.py  --> ShapeClipRaster( shapefile_filename,  FLAT, FLON, srcArray, resolutionX=0.25, resolutionY=0.25)
                                        根据输入的矢量数据对栅格数据进行裁剪，最后返回裁剪后的栅格数据


source
          |-->  boundary.shp
          |-->  china_boundary_polygon.shp
          |-->  china_province_polygon.shp
          |-->  global_country_boundary.shp





