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
# convert_query.py
#
# *3) Converts data (called as a sub-process to enable multiple simultaneous conversions with python)
#
#****************************************************

import time
import sqlite3
import visuspy as Visus
import VisusIdxPy
import VisusDbPy
import VisusKernelPy
#import SocketServer
#import BaseHTTPServer
#import fcntl
import cdms2
#import urlparse
import os
#import socket
#from sys import stdout
#from shutil import rmtree
#import cdat_to_idx


RESULT_SUCCESS=200; RESULT_INVALID=400; RESULT_NOTFOUND=404; RESULT_ERROR=500; RESULT_BUSY=503

def lookup_cdat_path(idxpath,dbpath):
    """lookup dataset corresponding to idxpath"""

    db=sqlite3.connect(dbpath)
    cur=db.cursor()
    if ".midx" in idxpath:
        cur.execute("SELECT ds_id from midxfiles where pathname=\"%s\"" % idxpath)
    else:
        cur.execute("SELECT ds_id from idxfiles where pathname=\"%s\"" % idxpath)
    cdatpath=cur.fetchall()
    #assert(len(cdatpath)<=1)  # shouldn't be dups, but for some early datasets (e.g. ganymed 2d) there are
    if len(cdatpath)>0:
        cur.execute("SELECT pathname from datasets where ds_id=%d" % cdatpath[0])
        cdatpath=cur.fetchone()[0]

        # <warning>
        # nasty hack to work around bug in cdms2 when using opendap:
        # solution is to run converter service from xml directory and
        # to load xml files from local paths, not explicit paths
        # (e.g. "filename.xml", not "/path/to/filename.xml".
        cdatpath=os.path.basename(cdatpath)
        return cdatpath,True
    return "",False


def read_cdat_data(cdatpath,field,timestep):
    """open and read a field from a cdat dataset"""
    f=cdms2.open(cdatpath)
    if not f.variables.has_key(field):
        raise ConvertError(RESULT_NOTFOUND,"Field %s not found in cdat volume %s."%(field,cdatpath))
    print cdatpath,"opened. Reading field",field,"at timestep",timestep
    v=f.variables[field]

    data=None
    has_time=v.getAxisList()[0].id.startswith("time")
    if has_time:
        if len(v) <= timestep or timestep<0:
            raise ConvertError(RESULT_NOTFOUND,"Timestep %d out of range for field %s."%(timestep,field))
        data=v[timestep]
    else:
        data=v
    print "finished reading field",field,"at timestep",timestep,"of",cdatpath

    #"flatten" masked data by inserting missing_value everywhere mask is invalid
    if isinstance(data,cdms2.tvariable.TransientVariable):
        data=data.filled()

    return data


def create_idx_query(idxpath,field,timestep,box,hz,dbpath):
    """open idx, validate inputs, create write query"""
    # we receive .midx path in query string. However, we need idx path to start conversion
    # since both .midx and .idx are created under the same basepath, just changing the extension from .midx to .idx is sufficient
    idxpath=os.path.dirname(dbpath)+"/"+idxpath
    idxpath=os.path.splitext(idxpath)[0]+'.idx'  

    dataset=VisusDbPy.Dataset.loadDataset(idxpath);
    if not dataset:
        raise ConvertError(RESULT_ERROR,"Error creating IDX query: could not load dataset "+idxpath)
    visus_field=dataset.get().getFieldByName(field);
    if not visus_field:
        raise ConvertError(RESULT_ERROR,"Error creating IDX query: could not find field "+field)

    access=dataset.get().createAccess()
    logic_box=dataset.get().getBox()

    if box or hz>=0:
        pass #print "TODO: handle subregion queries and resolution selection (box=%s,hz=%d)"%(box,hz)

    # convert the field
    query=VisusDbPy.QueryPtr(VisusDbPy.Query(dataset.get(), ord('w')))
    query.get().position=Visus.Position(logic_box)
    query.get().field=visus_field
    query.get().time=timestep

    dataset.get().beginQuery(query)

    return dataset,access,query  # IMPORTANT: need to return dataset,access because otherwise they go out of scope and query fails

class ConvertError(Exception):
    """Exception raised for errors during converstion.

    Attributes:
        ret  -- http return code for the exception
        msg  -- explanation of the error
    """
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
    def __str__(self):
        return "error "+self.code+": "+self.msg


def convert(idxpath,field,timestep,box,hz,dbpath):
    """Converts a timestep of a field of a cdat dataset to idx, using the idxpath to find the matching cdat volume."""
    VisusIdxPy.IdxModule.attach()

    t1  = time.time()
    pt1 = time.clock()

    # lookup dataset corresponding to idxpath
    cdatpath,success=lookup_cdat_path(idxpath,dbpath)
    if not success:
        result_str="Database does not list associated cdat dataset for %s"%idxpath
        print "-c;"+str(RESULT_NOTFOUND)+";-s;\\\""+result_str+"\\\""
        #return (result_str,RESULT_NOTFOUND)
        #sys.exit(0)  #(implied)

    # try to read lock file (note: this is unix-only)
    lockfilename="/tmp/"+idxpath+"-"+field+"-"+str(timestep)+".lock" #+"-"+str(box)+"-"+str(hz)+".lock" (for now, regions are ignored)
    lock=None
    result=RESULT_SUCCESS
    result_str="Success!"
    try:
        # get file lock
        print "opening lockfile:",lockfilename
        lock=os.open(lockfilename,os.O_CREAT|os.O_EXCL)

        #import pdb; pdb.set_trace()

        # open cdat, read the data
        # we receive field in this format output=input[<datasetname>].<fieldname>
        # we need extract the fieldname and pass this to read_cdat_data
        if "output" in field:
            field_name=field.split('.')[-1]
            field_name=field_name[:-1]
        else:
            field_name=field
        print "reading cdat data for field",field_name,"at time",timestep,"of",cdatpath
        data=read_cdat_data(cdatpath,field_name,timestep)

        # open idx and create query
        print "creating idx query for field",field_name,"at time",timestep,"of",cdatpath
        dataset,access,query=create_idx_query(idxpath,field_name,timestep,box,hz,dbpath)

        # validate bounds
        if data.size!=query.get().nsamples.innerProduct():
            raise ConvertError(RESULT_ERROR,"Invalid IDX query")
            
        # validate shape
        shape=data.shape[::-1]
        for i in range(len(shape)):
            if shape[i]!=query.get().nsamples[i]:
                raise ConvertError(RESULT_ERROR,"Invalid query dimensions.")
                
        # convert data
        print "converting field",field_name,"at time",timestep,"of",cdatpath,"to idx..."
        buffer=VisusKernelPy.convertToVisusArray(data)
        query.get().buffer=buffer.get()
        ret=dataset.get().executeQuery(access, query)

        if not ret:
            raise ConvertError(RESULT_ERROR,"Error executing IDX query.")
        print "done converting field",field_name,"at time",timestep,"of",cdatpath
            
    except IOError as e:
        if e.errno==None:
            result=RESULT_ERROR
            result_str="Error reading data. Please ensure cdms2 is working and NetCDF data is accessible."
        else:
            result=RESULT_ERROR
            result_str="An unknown i/o error has occured (e.errno="+os.strerror(e.errno)+")"
    except cdms2.CDMSError as e:
        result=RESULT_ERROR
        result_str="CDMSError: %s"%e
    except ConvertError as e:
        result=e.code
        result_str=e.msg
    except MemoryError as e:
        result_str="MemoryError: please try again ("+str(e)+")"
        result=RESULT_ERROR
    except Exception as e:
        if hasattr(e,"errno") and e.errno==17:
            result=RESULT_BUSY
            result_str="Conversion of field "+field+" at time "+str(timestep)+" in progress. Duplicate request ignored. (e.errno="+os.strerror(e.errno)+")"
        else:
            result=RESULT_ERROR
            result_str="unknown error occurred during convert ("+str(e)+")"
    finally:
        if lock:
            os.close(lock)
            os.remove(lockfilename)

    proctime=time.clock()-pt1
    interval=time.time()-t1
    if result==RESULT_SUCCESS:
        print("Total time to convert field "+field+" at time "+str(timestep)+" of "+cdatpath+" was %d msec (proc_time: %d msec)"  % (interval*1000,proctime*1000))
        
    return (result_str,result)
    # from sys import stdout
    # stdout.write("-c;"+str(result)+";-s;\\\""+result_str+"\\\"")
    # stdout.flush()


# ############################
if __name__ == '__main__':

    idxpath,field,timestep,box,hz

    import argparse
    parser = argparse.ArgumentParser(description="Convert CDAT data to IDX format.")
    parser.add_argument("-t","--timestep",default=0,type=int,help="timestep to convert")
    parser.add_argument("-z","--hz"      ,default=0,type=int,help="hz resolution to convert (currently ignored)")
    parser.add_argument("-b","--box"     ,default="",        help="region to convert (currently ignored)")
    parser.add_argument("-f","--field"   ,default="",        help="field to convert")
    parser.add_argument("-i","--idxpath" ,default="",        help="destination idx volume")
    args = parser.parse_args()

    out=convert(args.idxpath,args.field,args.timestep,args.box,args.hz)
    print out
