#!/usr/bin/env python

import time
import cdat_converter_service as ccs
ccs.init(database="/scratch/for_ganzberger1/idx/ondemand/idx/idx.db",hostname="none",port=80,xmlpath="/scratch/for_ganzberger1/idx/ondemand/xml",idxpath="/scratch/for_ganzberger1/idx/ondemand/idx",visus_server="none",username="user",password="pass")

idxpath="inst30mn_2d_aer1_Nx_M01-lon_lat_time.idx"
field="SUANGSTR"
box="" #ignored
hz=1   #ignored
for i in range(1344):
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
