#coding:utf-8
import os
import sys

China_Max_Lat = 60.0
China_Min_Lat = 0.0
China_Max_Lon = 140.0
China_Min_Lon = 70.0

xresolut = 0.05
yresolut = 0.05

glb_X_Resolution = 0.25
glb_Y_Resolution = 0.25


Root_Path = r'D:/FY4LMI'

PATH_1MinFile = os.path.join(Root_Path, r'data/input/LMIE')

PATH_1MinOut = os.path.join(Root_Path, r'data/result/1min')

PATH_L3_File = os.path.join(Root_Path, r'data/input/L3')

PATH_OUT_Density = os.path.join(Root_Path, r'data/result/density')

# 长时间序列文件目录
PATH_TimeList = os.path.join(Root_Path, r'data/result/1min/')

PATH_Input_ADTD = os.path.join(Root_Path, 'data', 'input', 'ADTD')

# 统计FY4A逐小时或逐分钟结果输出目录
PATH_Result_FY4A_LMIE = os.path.join(Root_Path, r'data/result/StatLMIEvents/FY4A_LMIE')

# 统计地基观测逐小时或逐分钟结果输出目录
PATH_Result_ADTD_LMIE = os.path.join(Root_Path, r'data/result/StatLMIEvents/ADTD_LMIE')

# FY4A与ADTD综合统计结果
PATH_Result_LMIE_Events = os.path.join(Root_Path, r'data/result/StatLMIEvents')

China_Mask_FileName = os.path.join(Root_Path, 'PAR','ChinaMask.HDF')

China_Province_Polygon = os.path.join(Root_Path, 'FY4LMI', 'source', 'china_province_polygon')


