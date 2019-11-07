#coding:utf-8
'''
逐小时统计FY4A 和ADTD LMI 闪电事件数
@author： libin
@e_mail: libin033@163.com
'''

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
from config import *


def StatADTDLMIEvent(filename, startime):
    Count = 0

    if not filename.endswith('.txt'):
        return Count

    data = np.loadtxt(filename,dtype=np.str)

    strtime = ["%s %s" %(x, y[0:8]) for x,y in zip(data[:, 1], data[:, 2])]

    sdate = [datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S') for x in strtime]
    sdate = np.array(sdate)

    endtime = startime + datetime.timedelta(hours=1)

    # print(startime, endtime)
    index = (sdate >= startime) & (sdate < endtime)
    s1 = sdate[index]
    Count = len(s1)

    return Count

def StatFY4ALMIEvent(filelist, mask=None):
    EventCount = 0
    for filename in filelist:
        if not os.path.isfile(filename):
            print('%s is not exist, will be continue...' %filename)
            continue

        if not filename.endswith('.NC'):
            print('%s is not a netcdf file, will be continue...' %filename)
            continue

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

        EventCount += np.count_nonzero(Flag)

    return EventCount

def StatHourGrade(strdate, WorkType = 1):

    if WorkType == 0 :
        return None
    dt = datetime.datetime.strptime(strdate, '%Y%m%d%H%M%S')




if __name__ == '__main__':
    #########################此处需要手动修改#######################################
    # FY4A LMIE L2数据
    # FY4A_LMI_PATH = r'./data/input/FY4A'
    FY4A_LMI_PATH = PATH_1MinFile

    # 地基观测数据
    # ADTD_PATH = r'./data/input/ADTD'
    ADTD_PATH = PATH_Input_ADTD

    # 输出结果文件名
    # txtname = r'./data/MinGrade.txt'

    # 输出结果路径
    # OutPath = './data/result'
    OutPath = PATH_Result_LMIE_Events

    # 处理的起始日期和结束日期
    strStarDate = '20180601000000'
    strEndDate = '20180602000000'
    ################################################################

    chinamask = ReadHDF(China_Mask_FileName, 'mask')
    argv = sys.argv
    if len(argv) == 3:
        s_time = datetime.datetime.strptime(argv[1], "%Y%m%d%H%M%S", )
        e_time = datetime.datetime.strptime(argv[2], "%Y%m%d%H%M%S")
    elif len(argv) == 2:
        s_time = datetime.datetime.strptime(argv[1], "%Y%m%d%H%M%S")
        e_time = datetime.datetime.strptime(argv[1], "%Y%m%d%H%M%S")
    else:
        s_time = datetime.datetime.strptime(strStarDate, "%Y%m%d%H%M%S")
        e_time = datetime.datetime.strptime(strEndDate, "%Y%m%d%H%M%S")

    print('It will do from %s to %s...' %(strStarDate, strEndDate))
    txtname = os.path.join(OutPath, '%s_%s_Hours.txt' % (s_time.strftime('%Y%m%d%H%M%S'), e_time.strftime('%Y%m%d%H%M%S')))
    fp = open(txtname, 'w')
    fp.close()

    dt = s_time
    while dt <= e_time:
        strdate = dt.strftime('%Y%m%d')

        # 处理FY4A闪电数据
        # LMIEPath = os.path.join(FY4A_LMI_PATH, dt.strftime('%Y'), dt.strftime('%Y%m%d'))
        LMIEPath = os.path.join(FY4A_LMI_PATH,  dt.strftime('%Y%m%d'))
        if not os.path.isdir(LMIEPath):
            LMIEPath = FY4A_LMI_PATH

        fils = glob.glob(os.path.join(LMIEPath, 'FY4A-_LMI---_N_REGX_1047E_L2-_LMIE_SING_NUL_%s*_N*V1.NC' %(dt.strftime('%Y%m%d%H'))))
        fils.sort()
        Count_LMI_FY4A = StatFY4ALMIEvent(fils, chinamask)

        # 处理地基闪电观测数据
        fils = glob.glob(os.path.join(ADTD_PATH, '%s.txt' % (dt.strftime('%Y_%m_%d'))))
        fils.sort()

        if len(fils) != 1:
            Count_LMI_ADTA = -999
        else:
            ADTD_FileName = fils[0]
            Count_LMI_ADTA = StatADTDLMIEvent(ADTD_FileName, dt)

        print('%-15s %8d %8d' %(dt.strftime('%Y%m%d%H%M%S'), Count_LMI_FY4A, Count_LMI_ADTA))
        fp = open(txtname, 'a')
        fp.write('%-15s %8d %8d\n' %(dt.strftime('%Y%m%d%H%M%S'), Count_LMI_FY4A, Count_LMI_ADTA))
        fp.close()

        # 逐小时递增
        dt = dt + datetime.timedelta(hours=1)







