#!/usr/bin/env python

import time
import cdat_converter_service as ccs
ccs.init(database="/scratch/for_ganzberger1/idx/ondemand/idx/idx.db",hostname="none",port=80,xmlpath="/scratch/for_ganzberger1/idx/ondemand/xml",idxpath="/scratch/for_ganzberger1/idx/ondemand/idx",visus_server="none",username="user",password="pass")

idxpaths=["inst30mn_2d_aer1_Nx_M01-lon_lat_time.idx","inst30mn_2d_aer1_Nx_M02-lon_lat_time.idx","inst30mn_2d_aer1_Nx_M03-lon_lat_time.idx","inst30mn_2d_aer1_Nx_M04-lon_lat_time.idx","inst30mn_2d_aer1_Nx_M05-lon_lat_time.idx","inst30mn_2d_aer1_Nx_M06-lon_lat_time.idx"]
field="SUANGSTR"
box="" #ignored
hz=1   #ignored
for i in range(1344):
    for idxpath in idxpaths:
        t1  = time.time()
        pt1 = time.clock()
        j=i*30 
        print("converting timestep "+str(j)+"...")

        (result_str,result)=ccs.convert(idxpath,field,j,box,hz)
        if not result==ccs.RESULT_SUCCESS:
            print result_str

        proctime=time.clock()-pt1
        interval=time.time()-t1
        print('   converted in time %d msec (proc_time: %d msec)'  % (interval*1000,proctime*1000))
