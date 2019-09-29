#coding:utf-8
import numpy as np
import os
import h5py


def WriteHDF(filename, sdsname, data,overwrite = 1, dictfileattrs=None, dictdsetattrs = None, dictgrpattrs = None):
    '''
    mode
    r Readonly, file must exist
    r+ Read/write, file must exist
    w Create file, truncate if exists
    w- or x Create file, fail if exists
    a Read/write if exists, create otherwise (default)
    :param filename:
    :param sdsname:
    :param data:
    :param overwrite:
    :return:
    '''
    if overwrite == 1:
        fout = h5py.File(filename,'w')
    else:
        fout = h5py.File(filename, 'a')

    # fout[sdsname] = data

    dsetis = fout.create_dataset(sdsname,  data=data)

    if not dictfileattrs is None:
        for key in dictfileattrs.keys():
            fout.attrs[key] = dictfileattrs[key]

    if not dictdsetattrs is None:
        for key in dictdsetattrs.keys():
            dsetis.attrs[key] = dictdsetattrs[key]

    fout.close()



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
