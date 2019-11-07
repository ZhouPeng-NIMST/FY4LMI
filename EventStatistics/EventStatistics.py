#coding:utf-8
'''
逐小时统计FY4A LMI 闪电事件数
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

xresolut = 0.05
yresolut = 0.05


def StatLMIEvent(filelist, mask=None):
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

def EventStat():
    return

if __name__ == '__main__':
    ################################################################
    # FY4A LMIE L2数据
    FY4A_LMI_PATH = r'./data/input/FY4A'

    # 地基观测数据
    ADTD_PATH = r'./data/input/ADTD'

    # 输出结果文件名
    # txtname = r'./data/MinGrade.txt'

    # 输出结果路径
    # OutPath = './data/'
    OutPath = PATH_Result_FY4A_LMIE

    # 处理的起始日期和结束日期
    strStarDate = '20180601000000'
    strEndDate = '20180701000000'
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

    print('It will do from %s to %s...' % (strStarDate, strEndDate))
    txtname = os.path.join(OutPath,
                           '%s_%s_Hours.txt' % (s_time.strftime('%Y%m%d%H%M%S'), e_time.strftime('%Y%m%d%H%M%S')))
    fp = open(txtname, 'w')
    fp.close()

    dt = s_time
    while dt <= e_time:
        strdate = dt.strftime('%Y%m%d')
        txtname = os.path.join(OutPath, '%s.txt' %(strdate))

        LMIEPath = os.path.join(FY4A_LMI_PATH, dt.strftime('%Y'), dt.strftime('%Y%m%d'))
        if not os.path.isdir(LMIEPath):
            LMIEPath = FY4A_LMI_PATH

        fils = glob.glob(os.path.join(LMIEPath, 'FY4A-_LMI---_N_REGX_1047E_L2-_LMIE_SING_NUL_%s*_N*V1.NC' %(dt.strftime('%Y%m%d%H'))))
        fils.sort()
        Count = StatLMIEvent(fils, chinamask)
        print('%s    %s' %(dt.strftime('%Y%m%d%H'),Count))
        fp = open(txtname, 'a')
        fp.write('%-15s %8d\n' %(dt.strftime('%Y%m%d%H%M%S'), Count))
        fp.close()
        dt = dt + datetime.timedelta(hours=1)




