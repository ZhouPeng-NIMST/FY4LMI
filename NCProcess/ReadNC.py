#coding:utf-8
import numpy as np
import netCDF4
import os


def ReadNC(filename, sdsname):
    if not os.path.isfile(filename):
        print('%s is not exist, will be exited!!!' %filename)
        exit(1)

    fin = netCDF4.Dataset(filename, 'r')
    data = fin.variables[sdsname][:]
    fin.close()

    return data




