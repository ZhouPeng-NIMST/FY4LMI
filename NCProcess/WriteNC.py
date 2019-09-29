#coding:utf-8
import numpy as np
import netCDF4


def WriteNC(filename, sdsname, data, overwrite = 1):
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
    data = np.array(data)
    if overwrite == 1:
        # 新建netcdf4 文件
        fout = netCDF4.Dataset(filename, 'w', format='NETCDF4')

        ndim = len(data.shape)
        if ndim == 1:
            fout.createDimension('x',data.shape[0])
            fout.createVariable('x','f',('x'))
            fout.variables['x'][:] = range(data.shape[0])

            fout.createVariable(sdsname, data.dtype, ('x'))
            fout.variables[sdsname][:] = data
        elif ndim == 2:
            fout.createDimension('x',data.shape[0])
            fout.createDimension('y',data.shape[1])
            fout.createVariable('x','f',('x'))
            fout.createVariable('y','f',('y'))
            fout.variables['x'][:] = range(data.shape[0])
            fout.variables['y'][:] = range(data.shape[1])

            fout.createVariable(sdsname, data.dtype, ('x','y'))
            fout.variables[sdsname][:] = data
        elif ndim == 3:
            fout.createDimension('z',data.shape[0])
            fout.createDimension('x',data.shape[1])
            fout.createDimension('y',data.shape[2])

            fout.createVariable('z','f',('z'))
            fout.createVariable('x','f',('x'))
            fout.createVariable('y','f',('y'))

            fout.variables['z'][:] = range(data.shape[0])
            fout.variables['x'][:] = range(data.shape[1])
            fout.variables['y'][:] = range(data.shape[2])

            fout.createVariable(sdsname, data.dtype, ('z','x','y'))
            fout.variables[sdsname][:] = data
        else:
            print("Input data(%d Dims) over the 3 Dims" %(ndim))
    else:
        # 在已存在的文件中追加数据集
        fout = netCDF4.Dataset(filename, 'a')
        ndim = len(data.shape)
        if ndim == 1:
            fout.createVariable(sdsname, data.dtype, ('x'))
            fout.variables[sdsname][:] = data
        elif ndim == 2:
            fout.createVariable(sdsname, data.dtype, ('x','y'))
            fout.variables[sdsname][:] = data
        elif ndim == 3:
            fout.createVariable(sdsname, data.dtype, ('z','x','y'))
            fout.variables[sdsname][:] = data
        else:
            print("Input data(%d Dims) over the 3 Dims" %(ndim))

    fout.close()
