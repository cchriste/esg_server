#!/usr/bin/env python

import os
import sys
import time
import cdat_converter_service as ccs

idxpaths={['BCANGSTR','BCCMASS','BCEXTTAU','BCSCATAU','BCSMASS','CO2CL001','CO2SC001','COCL','COSC','DMSCMASS','DMSSMASS','DUANGSTR','DUCMASS','DUCMASS25','DUEXTT25','DUEXTTAU','DUSCAT25','DUSCATAU','DUSMASS','DUSMASS25','OCANGSTR','OCCMASS','OCEXTTAU','OCSCATAU','OCSMASS','SO2CMASS','SO2SMASS','SO4CMASS','SO4SMASS','SSANGSTR','SSCMASS','SSCMASS25','SSEXTT25','SSEXTTAU','SSSCAT25','SSSCATAU','SSSMASS','SSSMASS25','SUANGSTR','SUEXTTAU','SUSCATAU','TOTANGSTR','TOTEXTTAU','TOTSCATAU']:["inst30mn_2d_aer1_Nx_M01-lon_lat_time.idx","inst30mn_2d_aer1_Nx_M02-lon_lat_time.idx","inst30mn_2d_aer1_Nx_M03-lon_lat_time.idx","inst30mn_2d_aer1_Nx_M04-lon_lat_time.idx","inst30mn_2d_aer1_Nx_M05-lon_lat_time.idx","inst30mn_2d_aer1_Nx_M06-lon_lat_time.idx"]}

field=sys.argv[1]

datasets=[]
for key in idxpaths:
    if field in key:
        datasets=idxpaths[key]
        break

if len(datasets)==0:
    print "no datasets found containing field "+field
    sys.exit(1)

ccs.init(database=os.environ['ONDEMAND_DB'],hostname="none",port=80,xmlpath=os.environ['ONDEMAND_XMLPATH'],idxpath=os.environ['ONDEMAND_IDXPATH'],visus_server="none")

box="" #ignored
hz=1   #ignored
for idxpath in idxpaths:
    timesteps=ccs.get_timesteps(idxpath)
    for i in timesteps:
        t1  = time.time()
        pt1 = time.clock()
        print("converting timestep "+str(i)+"...")

        (result_str,result)=ccs.convert(idxpath,field,i,box,hz)
        if not result==ccs.RESULT_SUCCESS:
            print result_str

        proctime=time.clock()-pt1
        interval=time.time()-t1
        print('   converted in time %d msec (proc_time: %d msec)'  % (interval*1000,proctime*1000))
