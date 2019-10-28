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

def StatLandLMI(filename, strdate):
    Count = 0

    if not filename.endswith('.txt'):
        return Count

    nowdate = datetime.datetime.strptime(strdate, '%Y_%m_%d')
    txtname = os.path.join('./data/LAND_LMIE', '%s.txt' % (nowdate.strftime('%Y%m%d')))
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
        fp.write('%-10s %8d\n' %(startime.strftime('%Y%m%d%H'), EventCount))
    fp.close()
    print(Count)






if __name__ == '__main__':
    pathin = r'D:\FY4LMI\EventStatistics\data\adtd201806'
    fils = os.listdir(pathin)
    fils.sort()

    for filename in fils:
        StatLandLMI(os.path.join(pathin, filename), filename.split('.')[0])




