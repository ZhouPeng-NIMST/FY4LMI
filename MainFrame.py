#coding:utf-8
"""
@author: libin
@create date: 2019-08-30
@
"""
import os
import sys
import numpy as np
import re
import datetime

exepath = os.path.dirname(__file__)
sys.path.append(os.path.join(exepath, '..'))
sys.path.append(os.path.join(exepath, '../..'))

from NCProcess import ReadNC, WriteNC
from HDFProcess import ReadHDF, WriteHDF

from DrawFY4LMI import *
from config import *


if __name__ == '__main__':
    argv = sys.argv
    if len(argv) == 3:
        s_time = datetime.datetime.strptime(argv[1], "%Y%m%d%H%M%S", )
        e_time = datetime.datetime.strptime(argv[2], "%Y%m%d%H%M%S")
    elif len(argv) == 2:
        s_time = datetime.datetime.strptime(argv[1], "%Y%m%d%H%M%S")
        e_time = datetime.datetime.strptime(argv[1], "%Y%m%d%H%M%S")
    else:
        s_time = datetime.datetime.strptime('20190520000000',"%Y%m%d%H%M%S")
        e_time = datetime.datetime.strptime('20190520000000', "%Y%m%d%H%M%S")

    ###############################################################################
    dt = s_time
    while dt <= e_time:
        # WorkType 为0，不执行；否则将执行
        strdate = dt.strftime('%Y%m%d%H%M%S')
        # step1: 做 1MIN 数据统计
        Stat1MinData(strdate, WorkType = 1)

        # step2: 合并文件
        CombFile(strdate, WorkType = 1)

        # step3: 绘制时间序列图
        DrawTimeList(strdate, WorkType = 1)

        # step4: 统计L3级文件，并绘制区域图像（日期匹配，定时调用）
        DrawREGNImage(strdate, WorkType = 1)
        # strdate = dt.strftime('%Y%m%d')
        # 拼接L2 1min 输入、输出目录
        # L2_1min_pathin = os.path.join( PATH_1MinFile, dt.strftime('%Y%m%d'))
        # L2_1min_pathout = os.path.join( PATH_1MinOut, dt.strftime('%Y%m%d'))
        # if not os.path.isdir(L2_1min_pathout):
        #     print('%s is not exist, will be created!!' %L2_1min_pathout)
        #     os.makedirs(L2_1min_pathout)
        #
        # L2_1min_HDFname = os.path.join(L2_1min_pathout, 'FY4A-_LMI---_L2-_LMIE_%s.HDF' % dt.strftime('%Y%m%d'))
        # # step1: 做 1MIN 数据统计
        # StatFile(dt.strftime('%Y%m%d'), L2_1min_pathin, L2_1min_HDFname)

        #step2: 合并文件
        # TimeListFileName = os.path.join(PATH_TimeList, 'FY4A-_LMI---_L2-_LMIE_TimeList.HDF')
        # CombFile(TimeListFileName, L2_1min_HDFname)

        # step3: 绘制时间序列图
        # filename = r'./data/result/1min/20190520/FY4A-_LMI---_L2-_LMIE_20190520_TimeList.HDF'
        # DrawTimeList(TimeListFileName)

        # 拼接L3级 输入、输出目录
        # L3_density_pathin = os.path.join( PATH_L3_File, dt.strftime('%Y%m%d'))
        # L3_density_pathin = PATH_L3_File
        #
        # # L3_density_pathout = os.path.join( PATH_OUT_Density, dt.strftime('%Y%m%d'))
        # L3_density_pathout = PATH_OUT_Density
        # if not os.path.isdir(L3_density_pathout):
        #     print('%s is not exist, will be created!!' %L3_density_pathout)
        #     os.makedirs(L3_density_pathout)
        #
        # # step4: 统计L3级文件，并绘制区域图像（日期匹配，定时调用）
        # Draw_LMI_REGX(dt, L3_density_pathin, L3_density_pathout)

        dt += datetime.timedelta(days=1)
