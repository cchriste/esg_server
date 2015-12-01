#***************************************************
#** ViSUS Visualization Project                    **
#** Copyright (c) 2010 University of Utah          **
#** Scientific Computing and Imaging Institute     **
#** 72 S Central Campus Drive, Room 3750           **
#** Salt Lake City, UT 84112                       **
#**                                                **
#** For information about this project see:        **
#** http:#www.pascucci.org/visus/                 **
#**                                                **
#**      or contact: pascucci@sci.utah.edu         **
#**                                                **
#****************************************************
#
#
# cdat_converter.py
#
# 1) Listens for http requests to convert a box of a timestep of a field of a dataset.
# 2) Ensures there are not already conversions in progress.
# 3) Converts data.
# 4) Signals caller upon completion.
#
#****************************************************
# Note:
#
# This is the less sophisticated version of cdat_converter, no threads, just
# file-based locking.  "Advantage" is that caller is blocked until conversion is
# complete.  But since caller is probably also threaded, this may be sufficient
# (it's not due to the extraordinary time needed to shut down python).
#
#****************************************************


import sqlite3
import sys
sys.path.append('/home/cam/code/nvisus/build/swig') 
import visuspy as Visus
from os import path,remove

def convert(idxpath,field,timestep,box,hz,db,datapath):
    """Converts a timestep of a field of a cdat dataset to idx, using the idxpath to find the matching cdat volume."""

    # lookup dataset corresponding to idxpath
    cur=db.cursor()
    cur.execute("SELECT ds_id from idxfiles where pathname=\"%s\"" % idxpath)
    cdatpath=cur.fetchall()
    assert(len(cdatpath)<=1)
    if len(cdatpath)>0:
        cur.execute("SELECT pathname from datasets where ds_id=%d" % cdatpath[0])
        cdatpath=cur.fetchone()[0]
    else:
        print "Unable to find associated cdat dataset for",idxpath
        return

    # try to read lock file (note: this is unix-only)
    import fcntl
    lockfilename=idxpath+"-"+field+"-"+str(timestep)+"-"+box+"-"+str(hz)+".lock"
    lockfile=open(lockfilename,"w")
    try:
        fcntl.lockf(lockfile,fcntl.LOCK_EX | fcntl.LOCK_NB)

        #import pdb; pdb.set_trace()

        # open cdat, read the data
        import cdms2
        f=cdms2.open(cdatpath)
        v=f.variables[field]
        has_time=v.getAxisList()[0].id=="time"
        data=None
        if has_time:
            data=v[timestep]
        else:
            data=v

        # open idx, convert the field
        dataset=Visus.Dataset.loadDataset(datapath+idxpath);  assert(dataset)
        visus_field=dataset.getFieldByName(field);            assert(field)
        access=dataset.createAccess()
        logic_box=dataset.getLogicBox()

        # validate bounds
        assert(data.size==logic_box.getDimension().innerProduct())
        shape=data.shape[::-1]
        for i in range(len(shape)):
            assert(shape[i]==logic_box.getDimension()[i])

        query=Visus.Query(dataset,ord('w'))
        query.setLogicPosition(Visus.Position(logic_box))
        query.setField(visus_field)
        query.setTime(timestep)
        query.setAccess(access)
        query.begin()
        assert(not query.end() and query.getNumberOfSamples().innerProduct()==data.size)

        visusarr=Visus.Array.fromNumPyArray(data)
        visusarrptr=Visus.ArrayPtr(visusarr)
        query.setBuffer(visusarrptr)
        ret=query.execute()
        assert(ret)
        print "done!"
    
    except IOError as e:
        #print "IOError({0}): {1}".format(e.errno,e.strerror)
        if e.errno==None:
            print "Error reading data. Please ensure cdms2 is working and NetCDF data is accessible."
        else:
            print "Could not acquire lock file: conversion may already be in progress. Returning."
    except cdms2.CDMSError as e:
        print "CDMSError:",e

    lockfile.close()
    remove(lockfilename)



# ############################
if __name__ == '__main__':

    app=Visus.Application()
    app.setCommandLine("")
    app.useModule(Visus.IdxModule.getSingleton())  

    import argparse
    parser = argparse.ArgumentParser(description="Convert CDAT data to IDX format.")
    parser.add_argument("-i","--idx",required=True,help="path to idx volume")
    parser.add_argument("-f","--field",required=True,help="field to read (e.g. ta)")
    parser.add_argument("-t","--time",required=True,type=int,help="timestep")
    parser.add_argument("-b","--box",default="",help="region to convert, default all")
    parser.add_argument("-r","--resolution",default=-1,type=int,help="hz level, default max")
    parser.add_argument("--database",default="",help="alternate cdat <--> idx database")
    args = parser.parse_args()

    # open idx db
    idxdb=args.database
    if len(idxdb)==0:
        idxdb=path.dirname(path.abspath(args.idx))+'/idx.db'
    db = sqlite3.connect(idxdb)

    with db:
        convert(path.basename(args.idx),args.field,args.time,args.box,args.resolution,db,path.dirname(idxdb)+"/")
