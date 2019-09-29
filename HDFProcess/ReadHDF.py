#coding:utf-8

import os
import h5py

def ReadHDF(filename, sdsname):
    data = []
    if not os.path.isfile(filename):
        print("%s not exist,will be returned!!!!" %(filename))
        return data

    with h5py.File(filename, "r") as fin:
        data = fin[sdsname][:]
        fin.close()

    return data


