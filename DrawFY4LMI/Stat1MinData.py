#coding:utf-8
import os
import numpy as np
import re
import sys
import datetime
import glob

exepath = os.path.dirname(__file__)
sys.path.append(os.path.join(exepath, '..'))
sys.path.append(os.path.join(exepath, '../..'))

from NCProcess import *
from HDFProcess import *
from config import *

def OutPutHDF(filename, NowTime, StarDatetime, EndDatetime, Num, Events):
    WriteHDF(filename, 'StarDatetime', StarDatetime, overwrite=1)
    WriteHDF(filename, 'EndDatetime', EndDatetime, overwrite=0)
    WriteHDF(filename, 'NowTime', NowTime, overwrite=0)
    WriteHDF(filename, 'Num', Num, overwrite=0)
    WriteHDF(filename, 'Events', Events ,overwrite=0)

def WriteTXT(filename, nowtime, namels, data, overwrite=1):

    if overwrite == 1:
        fout = open(filename, 'w')
        # 增加写头
        fout.write('{0:15}{1:15}{2:15}{3:15}{4:15}'.format('NowTime','StarDatetime', 'EndDatetime', 'Num', 'Events'))
    else:
        fout = open(filename, 'a')
    fout.write('\n')
    fout.write('{0:15}{1:15}{2:15}{3:15}{4}'.format(nowtime, namels[9], namels[10], namels[12][1:3], data))

    fout.close()

def StatFile(strdate, pathin=None, outHDFname=None, flag = 1):
    '''
    统计一天的闪电数据
    :param strdate: 日期
    :param pathin:
    :param pathout:
    :param flag:
    :return:
    '''

    # fils = os.listdir(pathin)

    # 拼接输入、输出文件名
    outPicName = outHDFname.replace('.HDF','.PNG')
    outTXTname = outHDFname.replace('.HDF','.TXT')

    seachname = os.path.join(pathin, 'FY4A-_LMI---_N_REGX_1047E_L2-_LMIE_SING_NUL_*_*_7800M_N*V1.NC')
    filels = glob.glob(seachname)
    # print(filels)
    filels.sort()
    DateTime = []
    StarDatetime = []
    EndDatetime = []
    Num = []
    Events =[]

    for filename in filels:
        # filename =r'E:\Personal\kangning\DATA\1MIN\FY4A-_LMI---_N_REGX_1047E_L2-_LMIE_SING_NUL_20190520000510_20190520001449_7800M_N01V1.NC'
        name = os.path.basename(filename)

        namels = re.split('_',name)

        # 读取ER数据
        ER = ReadNC(filename, 'ER')

        # 从文件名中获取观测起始、结束时间，观测点ID，事件数量
        StarDatetime.append(int(namels[9]))
        EndDatetime.append(int(namels[10]))
        Num.append(int(namels[12][1:3]))
        Events.append(ER.shape[0])

        D_time = datetime.datetime.strptime(namels[9], "%Y%m%d%H%M%S")
        D_time += datetime.timedelta(minutes = int(namels[12][1:3]))
        strtime = D_time.strftime("%Y%m%d%H%M%S")
        DateTime.append(int(strtime))
        # 写TXT文件
        WriteTXT(outTXTname, strtime, namels, ER.shape[0], flag)
        flag = 0

    print("%s write success!!!" %outTXTname)
    # StarDatetime = np.array(StarDatetime, dtype = 'S20')
    # EndDatetime = np.array(EndDatetime, dtype = 'S20')
    # 输出HDF文件
    OutPutHDF(outHDFname, DateTime, StarDatetime, EndDatetime, Num, Events)
    print("%s write success!!!" %outHDFname)


def Stat1MinData(strdate, WorkType = 1):
    '''

    :param strdate:
    :param WorkType:
    :return:
    '''
    if WorkType == 0 :
        return None
    dt = datetime.datetime.strptime(strdate, '%Y%m%d%H%M%S')
    L2_1min_pathin = os.path.join(PATH_1MinFile, dt.strftime('%Y%m%d'))
    L2_1min_pathout = os.path.join(PATH_1MinOut, dt.strftime('%Y%m%d'))
    if not os.path.isdir(L2_1min_pathout):
        print('%s is not exist, will be created!!' % L2_1min_pathout)
        os.makedirs(L2_1min_pathout)

    L2_1min_HDFname = os.path.join(L2_1min_pathout, 'FY4A-_LMI---_L2-_LMIE_%s.HDF' % dt.strftime('%Y%m%d'))
    StatFile(dt.strftime('%Y%m%d'), L2_1min_pathin, L2_1min_HDFname)
    print('Static 1 Minute Data Success...')

if __name__ == '__main__':
    argv = sys.argv
    if len(argv) == 3:
        s_time = datetime.datetime.strptime(argv[1], "%Y%m%d", )
        e_time = datetime.datetime.strptime(argv[2], "%Y%m%d")
    elif len(argv) == 2:
        s_time = datetime.datetime.strptime(argv[1], "%Y%m%d")
        e_time = datetime.datetime.strptime(argv[1], "%Y%m%d")
    else:
        s_time = datetime.datetime.strptime('20190520',"%Y%m%d")
        e_time = datetime.datetime.strptime('20190520', "%Y%m%d")

    flag = 1
    dt = s_time
    while dt <= e_time:
        strdate = dt.strftime('%Y%m%d')
        pathin = os.path.join( r'../data/1MIN', strdate)
        pathin = r'../data/1MIN'

        StatFile(strdate, pathin, flag=1)
        flag = 0
        dt += datetime.timedelta(days=1)