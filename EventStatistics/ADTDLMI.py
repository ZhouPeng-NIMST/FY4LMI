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

from config import *

def StatLandLMI(filename, strdate, OutPath):
    Count = 0

    if not filename.endswith('.txt'):
        return Count

    nowdate = datetime.datetime.strptime(strdate, '%Y_%m_%d')
    txtname = os.path.join(OutPath, '%s.txt' % (nowdate.strftime('%Y%m%d')))
    fp = open(txtname, 'w')
    data = np.loadtxt(filename,dtype=np.str)
    print(data.shape)
    strtime = ["%s %s" %(x, y[0:8]) for x,y in zip(data[:, 1], data[:, 2])]

    sdate = [datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S') for x in strtime]
    sdate = np.array(sdate)
    for i in range(24):
        startime = nowdate + datetime.timedelta(hours=i)
        endtime = nowdate + datetime.timedelta(hours=i+1)

        # print(startime, endtime)
        index = (sdate >= startime) & (sdate < endtime)
        s1 = sdate[index]
        EventCount = len(s1)
        Count += EventCount
        print(startime, EventCount)
        fp.write('%-15s %8d\n' %(startime.strftime('%Y%m%d%H%M%S'), EventCount))
    fp.close()
    print(Count)






if __name__ == '__main__':
    #############################################################
    # FY4A LMIE L2数据
    # FY4A_LMI_PATH = r'./data/input/FY4A'
    FY4A_LMI_PATH = PATH_1MinFile

    # 地基观测数据
    # ADTD_PATH = r'./data/input/ADTD'
    ADTD_PATH = PATH_Input_ADTD

    # 结果输出目录
    # OutPath = r'./data/result/ADTD_LMIE'
    OutPath = PATH_Result_ADTD_LMIE
    ############################################################
    fils = os.listdir(ADTD_PATH)
    fils.sort()

    for filename in fils:
        if filename.endswith('.txt'):
            StatLandLMI(os.path.join(ADTD_PATH, filename), filename.split('.')[0], OutPath)




