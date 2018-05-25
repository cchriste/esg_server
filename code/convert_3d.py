#!/usr/bin/env python

import time
import cdat_converter_service as ccs
ccs.init(database="/data/idx/idx.db",hostname="none",port=80,xmlpath="/data/xml",idxpath="/data/idx",visus_server="none")

idxpaths=["nasa3d-lon_lat_lev_time.idx"]
field="CO2"
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
