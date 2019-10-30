#coding:utf-8
import os
import sys
import datetime
import glob
import numpy as np
exepath = os.path.dirname(__file__)
sys.path.append(os.path.join(exepath, '..'))
sys.path.append(os.path.join(exepath, '../..'))

from NCProcess import ReadNC, WriteNC
from HDFProcess import ReadHDF, WriteHDF

xresolut = 0.05
yresolut = 0.05

def AnalysisFY4AFile(filelist):
    dictfile = {}
    for filename in filelist:
        namels = filename.split('_')
        strtime = datetime.datetime.strptime(namels[9][0:12], '%Y%m%d%H%M')
        strtime += datetime.timedelta(minutes= float(namels[12][1:3]) - 1)
        # print(strtime, os.path.basename(filename))
        key = strtime.strftime('%Y%m%d%H%M')
        if not key in dictfile:
            dictfile.update({ key : filename})
        else:
            print('~'*100)

    return dictfile

def StatLMIEvent(filename, mask=None):
    '''
    统计卫星观测闪电
    :param filelist:
    :param mask:
    :return:
    '''
    EventCount = -888

    if not os.path.isfile(filename):
        print('%s is not exist, will be continue...' %filename)
        return EventCount

    if not filename.endswith('.NC'):
        print('%s is not a netcdf file, will be continue...' %filename)
        return EventCount

    Data_Lat = ReadNC(filename, 'LAT')
    Data_Lon = ReadNC(filename, 'LON')
    Line = (60.0 - Data_Lat) / yresolut + 0.5
    Col = (Data_Lon - 70.0) / xresolut + 0.5
    Line = Line.astype(np.int32)
    Col = Col.astype(np.int32)

    index = np.where(Line < mask.shape[0])
    Line = Line[index]
    Col = Col[index]
    index = np.where(Col < mask.shape[1])
    Line = Line[index]
    Col = Col[index]

    Flag = mask[Line, Col]

    EventCount = np.count_nonzero(Flag)

    return EventCount

def StatLandLMI(filename):
    '''
    统计地基观测闪电
    :param filename:
    :param strdate:
    :return:
    '''
    Count = 0
    if not filename.endswith('.txt'):
        return Count

    data = np.loadtxt(filename,dtype=np.str)

    strtime = ["%s %s" %(x, y[0:8]) for x,y in zip(data[:, 1], data[:, 2])]

    sdate = [datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S') for x in strtime]
    sdate = np.array(sdate)

    return sdate

if __name__ == '__main__':

    ################################################################
    # FY4A LMIE L2数据
    FY4A_LMI_PATH = r'Z:\FY4A\LMI\L2\LMIE\REGX'

    # 地基观测数据
    ADTD_PATH = r'D:\FY4LMI\EventStatistics\data\adtd201806'

    # 输出结果文件名
    txtname = r'./data/MinGrade.txt'

    # 处理的起始日期和结束日期
    strStarDate = '20180601'
    strEndDate = '20180701'
    ################################################################

    argv = sys.argv
    if len(argv) == 3:
        s_time = datetime.datetime.strptime(argv[1], "%Y%m%d", )
        e_time = datetime.datetime.strptime(argv[2], "%Y%m%d")
    elif len(argv) == 2:
        s_time = datetime.datetime.strptime(argv[1], "%Y%m%d")
        e_time = datetime.datetime.strptime(argv[1], "%Y%m%d")
    else:
        s_time = datetime.datetime.strptime(strStarDate, "%Y%m%d")
        e_time = datetime.datetime.strptime(strEndDate, "%Y%m%d")

    # 获取掩膜数据
    chinamask = ReadHDF(r'../ShapeClipRaster/ChinaMask.HDF', 'mask')
    fp = open(txtname, 'w')
    fp.close()
    dt = s_time
    while dt <= e_time:
        print(dt)
        # 统计FY4A的闪电
        LMIEPath = os.path.join(FY4A_LMI_PATH, dt.strftime('%Y'), dt.strftime('%Y%m%d'))
        FY4A_fils = glob.glob(os.path.join(LMIEPath, 'FY4A-_LMI---_N_REGX_1047E_L2-_LMIE_SING_NUL_%s*_N*V1.NC' % (
            dt.strftime('%Y%m%d'))))
        FY4A_fils.sort()
        dictfile = AnalysisFY4AFile(FY4A_fils)
        # Count = StatLMIEvent(FY4A_fils, chinamask)
        # print('%s    %s' % (dt.strftime('%Y%m%d%H'), Count))

        ADTA_FileName = os.path.join(ADTD_PATH, '%s.txt' %(dt.strftime('%Y_%m_%d')))
        if os.path.isfile(ADTA_FileName):
            sdate = StatLandLMI(ADTA_FileName)

        istar = dt
        iend = dt + datetime.timedelta(hours=1)
        while istar < iend:
            key = istar.strftime('%Y%m%d%H%M')

            if key in dictfile:
                Count_FY4A_LMIE = StatLMIEvent(dictfile[key],  chinamask)
            else:
                print(key, dictfile)
                Count_FY4A_LMIE = -999

            # 统计地基观测闪电
            if os.path.isfile(ADTA_FileName):
                index = (sdate >= istar) & (sdate < istar+datetime.timedelta(minutes=1))
                s1 = sdate[index]
                Count_ADTD_LMIE = len(s1)
            else:
                Count_ADTD_LMIE = -999
            fp = open(txtname, 'a')
            fp.write('%-12s %8d %8d\n' % (istar.strftime('%Y%m%d%H%M'), Count_FY4A_LMIE, Count_ADTD_LMIE))
            fp.close()
            istar += datetime.timedelta(minutes=1)

        dt = dt + datetime.timedelta(hours=1)




