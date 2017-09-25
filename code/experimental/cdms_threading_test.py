"""
Test that demonstrates cdms2 operating in multithreaded mode.
Current result is thread "safe" but actually serializes tasks.
"""


import cdms2
import threading

def reader(cdatpath,field,timestep):
    """open and read a field from cdms dataset"""
    f=cdms2.open(cdatpath)
    v=f.variables[field]
    data=v[timestep]
    print "thread",threading.currentThread().getName(),data.shape
    return

# def ornl_reader(cdatpath,field,timestep):
#     """open and read a field from cdms dataset"""
#     f=cdms2.open(cdatpath)
#     v=f.variables[field]
#     data=v[0][timestep]
#     print "thread",threading.currentThread().getName(),data.shape
#     return

threads=[]
for i in range(12):
    args=("nasa_ganymed_7km_2d.xml","sscmass25",i,)
    t=threading.Thread(target=reader,args=args)
    threads.append(t)
    t.start()

    args=("acme-test.ORNL.HIGHRES.init.all.v1.xml","QC",i,)
    t=threading.Thread(target=reader,args=args)
    threads.append(t)
    t.start()

    # args=("ornl_opendap_test.xml","CCN3",i,)
    # t=threading.Thread(target=ornl_reader,args=args)
    # threads.append(t)
    # t.start()

