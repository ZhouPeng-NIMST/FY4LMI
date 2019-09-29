#coding:utf-8
import os
import sys
import matplotlib
import matplotlib.pyplot as plt
import datetime
from matplotlib.dates import DateFormatter, MonthLocator, DayLocator, YearLocator,HourLocator,MinuteLocator
from matplotlib.dates import AutoDateLocator, AutoDateFormatter,date2num
exepath = os.path.dirname(__file__)
sys.path.append(os.path.join(exepath, '..'))
sys.path.append(os.path.join(exepath, '../..'))

from NCProcess import *
from HDFProcess import *


def DrawTimeListPic(outfilename, NowTime, Events ):

    s_time = np.nanmin(NowTime) - datetime.timedelta(seconds = 60*7)
    e_time = np.nanmax(NowTime)  + datetime.timedelta(seconds = 60*7)

    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111)

    ax.plot(NowTime, Events, '-',color='k', lw=0.6)

    # 设置轴的范围
    ax.set_xlim(s_time, e_time)

    # 设置时间轴
    delta=e_time - s_time       # 计算起始、结束时间差
    mindays=datetime.timedelta(5)
    if delta<mindays:
        ss=(delta -mindays)/2 + s_time
        ee=(mindays-delta)/2 + e_time
    else:
        halfday=datetime.timedelta(hours=12)
        ss=s_time - halfday
        ee=e_time + halfday*3

    x_locator = AutoDateLocator(minticks=2, maxticks=8, interval_multiples=True)  #
    x_format = AutoDateFormatter(x_locator, defaultfmt='%Y-%m-%d\n%H:%M')
    x_format.scaled = {
        0.5:    u'%Y-%m-%d\n%H:%M',
        1.0:    u'%Y-%m-%d',
        30.0:   u'%Y-%m',
        365.0:  u'%Y'
    }
    ax.xaxis.set_major_formatter(x_format)
    ax.xaxis.set_major_locator(x_locator)
    # if strType == 'TD' :
    #     predays = 91
    #     ax.set_xlim( *date2num([e_time-datetime.timedelta(days=predays),e_time+datetime.timedelta(days=1)] ))
    # elif strType == 'AM' or strType == 'AQ':
    #     predays = 366
    #     ax.set_xlim( *date2num([e_time-datetime.timedelta(days=predays),e_time+datetime.timedelta(days=1)] ))
    # elif strType == 'AY' :
    #     ax.set_xlim(ss-datetime.timedelta(days=1), ee+datetime.timedelta(days=1))


    #
    # # 主刻度
    # formatter = DateFormatter('%H')
    # ax.xaxis.set_major_formatter(formatter)
    # ax.xaxis.set_major_locator(HourLocator(interval=1))
    #
    # # 次刻度
    # ax.xaxis.set_minor_formatter(DateFormatter('%M'))
    # ax.xaxis.set_minor_locator(MinuteLocator(interval=3))

    # plt.show()
    plt.savefig(outfilename, dpi = 200,)



def DrawTimeList(filename ):
    '''
    绘制1分钟时间序列图
    :param filename:
    :return:
    '''
    NowTime = ReadHDF(filename, 'NowTime')
    Events = ReadHDF(filename, 'Events')

    Data_NowTime = [datetime.datetime.strptime(str(i), "%Y%m%d%H%M%S") for i in NowTime]

    outfilename = filename.replace('.HDF', '.PNG')
    DrawTimeListPic(outfilename, Data_NowTime, Events )


if __name__ == '__main__':
    filename = r'../data/FY4A-_LMI---_L2-_LMIE_20190520.HDF'
    DrawTimeList(filename)
