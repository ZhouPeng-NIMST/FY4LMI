#coding:utf-8
import os
import sys
import datetime

exepath = os.path.dirname(__file__)
sys.path.append(os.path.join(exepath, '..'))
sys.path.append(os.path.join(exepath, '../..'))

from NCProcess import *
from HDFProcess import *
from config import *

def CombFile1(fils, outname):

    # 对文件进行排序
    fils.sort()

    NowTime = []
    StarDatetime = []
    EndDatetime = []
    Num = []
    Events = []

    for filename in fils:
        print(filename)
        data1 = ReadHDF(filename, 'NowTime')
        data2 = ReadHDF(filename, 'StarDatetime')
        data3 = ReadHDF(filename, 'EndDatetime')
        data4 = ReadHDF(filename, 'Num')
        data5 = ReadHDF(filename, 'Events')

        NowTime = np.hstack([NowTime, data1])
        StarDatetime = np.hstack([StarDatetime, data2])
        EndDatetime = np.hstack([EndDatetime, data3])
        Num = np.hstack([Num, data4])
        Events = np.hstack([Events, data5])


    WriteHDF(outname, 'StarDatetime', StarDatetime, overwrite=1)
    WriteHDF(outname, 'EndDatetime', EndDatetime, overwrite=0)
    WriteHDF(outname, 'NowTime', NowTime, overwrite=0)
    WriteHDF(outname, 'Num', Num, overwrite=0)
    WriteHDF(outname, 'Events', Events ,overwrite=0)

def CombFile(strdate, WorkType = 1):

    if WorkType == 0 :
        return None
    dt = datetime.datetime.strptime(strdate, '%Y%m%d%H%M%S')
    L2_1min_pathout = os.path.join( PATH_1MinOut, dt.strftime('%Y%m%d'))
    if not os.path.isdir(L2_1min_pathout):
        print('%s is not exist, will be created!!' %L2_1min_pathout)
        os.makedirs(L2_1min_pathout)
    L2_1min_HDFname = os.path.join(L2_1min_pathout, 'FY4A-_LMI---_L2-_LMIE_%s.HDF' % dt.strftime('%Y%m%d'))
    TimeListFileName = os.path.join(PATH_TimeList, 'FY4A-_LMI---_L2-_LMIE_TimeList.HDF')

    if not os.path.isfile(TimeListFileName):
        fp1 = h5py.File(TimeListFileName, 'w')
    else:
        fp1 = h5py.File(TimeListFileName, 'a')

    if not os.path.isfile(L2_1min_HDFname):
        return 1
    else:
        fp2 = h5py.File(L2_1min_HDFname, 'r')

    for key in fp2.keys():
        if not key in fp1.keys():
            data2 = fp2[key][:]
            print(data2)
            # maxshape=(None,)*(data2.ndim if data2 else 1)
            dst=fp1.create_dataset(key, data=data2, maxshape=(None,),compression=5)
        else:
            data1 = fp1[key]
            data2 = fp2[key]
            m = data1.shape[0]
            n = data2.shape[0]
            data1.resize(size=m + n, axis=0)
            data1[m:] = data2

    fp1.close()
    fp2.close()

    print('Combine <<%s>> and <<%s>>  Success...' %(TimeListFileName, L2_1min_HDFname))

def writedataset(out,name,data=None,fillvalue=-999999.0):
    if name in out:
        dset = out[name]
        #######################################
        if len(dset.shape) == 2:
            if dset.shape[1] != data.shape[1]:
                #print('*****name:%s dset.shape[1]:%d ,data.shape[1]:%d*************' %(name,dset.shape[1], data.shape[1]))
                if dset.shape[1] > data.shape[1]:
                    maxshape = dset.shape[1]
                else:
                    maxshape = data.shape[1]

                if dset.shape[1] > data.shape[1]:
                    tempdata = np.full((data.shape[0],maxshape), fillvalue, dtype=dset.dtype)
                    tempdata[0:data.shape[0], 0:data.shape[1]] = data

                    n = dset.shape[0]
                    dset.resize(size=n+1,axis=0)
                    if data is None:
                        dset[n]=fillvalue
                    else:
                        dset[n]=tempdata
                else:
                    tempdata = np.full((dset.shape[0]+1,maxshape), fillvalue, dtype=dset.dtype)
                    tempdata[0:dset.shape[0], 0:dset.shape[1]] = dset
                    tempdata[dset.shape[0]:dset.shape[0]+data.shape[0],0:data.shape[1]] = data
                    dset.resize((dset.shape[0]+1,maxshape))
                    dset[:] = tempdata
                return 0
        elif len(dset.shape) == 3:
            if dset.shape[1] != data.shape[1] or dset.shape[2] != data.shape[2]:
                #print '*****dset.shape[1]:%d ,data.shape[1]:%d,dset.shape[2]:%d, data.shape[2]:%d*************' %(dset.shape[1], data.shape[1],dset.shape[2], data.shape[2])
                if dset.shape[1] > data.shape[1]:
                    maxshape1 = dset.shape[1]
                else:
                    maxshape1 = data.shape[1]

                if dset.shape[2] > data.shape[2]:
                    maxshape2 = dset.shape[2]
                else:
                    maxshape2 = data.shape[2]

                if maxshape1 > data.shape[1] and maxshape2 > data.shape[2]:
                    tempdata = np.full((data.shape[0],maxshape1, maxshape2), fillvalue, dtype=dset.dtype)
                    tempdata[0:data.shape[0], 0:data.shape[1], 0:data.shape[2]] = data

                    n = dset.shape[0]
                    dset.resize(size=n+1,axis=0)
                    if data is None:
                        dset[n]=fillvalue
                    else:
                        dset[n]=tempdata
                else:
                    tempdata = np.full((dset.shape[0]+1,maxshape1, maxshape2), fillvalue, dtype=dset.dtype)
                    tempdata[0:dset.shape[0], 0:dset.shape[1], 0:dset.shape[2]] = dset
                    tempdata[dset.shape[0]:dset.shape[0]+data.shape[0],0:data.shape[1],0:data.shape[2]] = data
                    dset.resize((dset.shape[0]+1, maxshape1, maxshape2))
                    dset[:] = tempdata
                return 0

        n = dset.shape[0]
        dset.resize(size=n+1,axis=0)
        if data is None:
            dset[n]=fillvalue
        else:
            dset[n]=data
    else:
        maxshape=(None,)*(data.ndim if data else 1)
        dst=out.create_dataset(name, data=data or [fillvalue], chunks=True,maxshape=maxshape, compression=9)
        if isinstance(data,h5py.Dataset):
            dst.attrs.update(data.attrs)



if __name__ == '__main__':
    pass



