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

if __name__ == '__main__':

    chinamask = ReadHDF(r'../ShapeClipRaster/ChinaMask.HDF', 'mask')
    pathin = r'Z:\FY4A\LMI\L2\LMIE\REGX'
    argv = sys.argv
    if len(argv) == 3:
        s_time = datetime.datetime.strptime(argv[1], "%Y%m%d", )
        e_time = datetime.datetime.strptime(argv[2], "%Y%m%d")
    elif len(argv) == 2:
        s_time = datetime.datetime.strptime(argv[1], "%Y%m%d")
        e_time = datetime.datetime.strptime(argv[1], "%Y%m%d")
    else:
        s_time = datetime.datetime.strptime('20180601', "%Y%m%d")
        e_time = datetime.datetime.strptime('20180701', "%Y%m%d")

    dt = s_time
    while dt <= e_time:
        strdate = dt.strftime('%Y%m%d')
        txtname = r'./data/%s.txt' %(strdate)
        if os.path.isfile(txtname):
            fp = open(txtname, 'a')
        else:
            fp = open(txtname, 'w')

        LMIEPath = os.path.join(pathin, dt.strftime('%Y'), dt.strftime('%Y%m%d'))

        fils = glob.glob(os.path.join(LMIEPath, 'FY4A-_LMI---_N_REGX_1047E_L2-_LMIE_SING_NUL_%s*_N*V1.NC' %(dt.strftime('%Y%m%d%H'))))
        fils.sort()
        Count = StatLMIEvent(fils, chinamask)
        print('%s    %s' %(dt.strftime('%Y%m%d%H'),Count))
        fp.write('%-10s %8d\n' %(dt.strftime('%Y%m%d%H'), Count))
        fp.close()
        dt = dt + datetime.timedelta(hours=1)




