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
# 1) Listens for http requests to convert a box of a resolution of a timestep of a field of a dataset.
# 2) Ensures there are not already conversions in progress.
# 3) Converts data.
# 4) Signals caller upon completion.
#
#****************************************************

import time
import sqlite3
import visuspy as Visus
import SocketServer
import BaseHTTPServer
import fcntl
import cdms2
import urlparse
from os import remove,path

RESULT_SUCCESS=200; RESULT_INVALID=400; RESULT_NOTFOUND=404; RESULT_ERROR=500; RESULT_BUSY=503

class cdatConverter(BaseHTTPServer.BaseHTTPRequestHandler):
    """http request handler for cdat to idx conversion requests"""

    def do_GET(self):
        url=urlparse.urlparse(self.path)
        if url.path=='/convert':
            result,response=convert(url.query)
            self.send_response(response)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(result)
            return


def lookup_cdat_path(idxpath):
    """lookup dataset corresponding to idxpath"""

    db=sqlite3.connect(dbpath)
    cur=db.cursor()
    cur.execute("SELECT ds_id from idxfiles where pathname=\"%s\"" % idxpath)
    cdatpath=cur.fetchall()
    assert(len(cdatpath)<=1)
    if len(cdatpath)>0:
        cur.execute("SELECT pathname from datasets where ds_id=%d" % cdatpath[0])
        cdatpath=cur.fetchone()[0]
        return cdatpath,True
    return "",False


def parse_query(query):
    """parse the cdat to idx conversion query string"""

    job=urlparse.parse_qs(query)
    idxpath=None
    field=None
    timestep=0
    box=None
    hz=-1
    if job.has_key("idx"):
        idxpath=job["idx"][0]
    if job.has_key("field"):
        field=job["field"][0]
    if job.has_key("time"):
        timestep=int(job["time"][0])
    if job.has_key("box"):
        box=job["box"][0]
    if job.has_key("hz"):
        hz=int(job["hz"][0])
    return idxpath,field,timestep,box,hz


def read_cdat_data(cdatpath,field,timestep):
    """open and read a field from a cdat dataset"""

    f=cdms2.open(cdatpath)
    if not f.variables.has_key(field):
        raise ConvertError(RESULT_NOTFOUND,"Field %s not found in cdat volume %s."%(field,cdatpath))
    v=f.variables[field]

    data=None
    has_time=v.getAxisList()[0].id=="time"
    if has_time:
        if len(v) <= timestep or timestep<0:
            raise ConvertError(RESULT_NOTFOUND,"Timestep %d out of range for field %s."%(timestep,field))
        data=v[timestep]
    else:
        data=v
    return data


def create_idx_query(idxpath,field,timestep,box,hz):
    """open idx, validate inputs, create write query"""

    global dbpath
    idxpath=path.dirname(dbpath)+"/"+idxpath
    dataset=Visus.Dataset.loadDataset(idxpath);
    if not dataset:
        raise ConvertError(RESULT_ERROR,"Error creating IDX query: could not load dataset "+idxpath)
    visus_field=dataset.getFieldByName(field);
    if not visus_field:
        raise ConvertError(RESULT_ERROR,"Error creating IDX query: could not find field "+field)
    access=dataset.createAccess()
    logic_box=dataset.getLogicBox()

    if box or hz>=0:
        print "TODO: handle subregion queries and resolution selection (box=%s,hz=%d)"%(box,hz)

    # convert the field
    query=Visus.Query(dataset,ord('w'))
    query.setLogicPosition(Visus.Position(logic_box))
    query.setField(visus_field)
    query.setTime(timestep)
    query.setAccess(access)
    query.begin()
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


def convert(query):
    """Converts a timestep of a field of a cdat dataset to idx, using the idxpath to find the matching cdat volume."""

    t1 = time.clock()

    # parse query request
    idxpath,field,timestep,box,hz=parse_query(query)
    if not idxpath or not field:
        return ("Invalid query: %s"%query,RESULT_INVALID)

    # lookup dataset corresponding to idxpath
    cdatpath,success=lookup_cdat_path(idxpath)
    if not success:
        return ("Database does not list associated cdat dataset for %s"%idxpath,RESULT_NOTFOUND)

    # try to read lock file (note: this is unix-only)
    lockfilename="/tmp/"+idxpath+"-"+field+"-"+str(timestep)+"-"+str(box)+"-"+str(hz)+".lock"
    lockfile=open(lockfilename,"w")
    result=RESULT_SUCCESS
    result_str="Success!"
    try:
        fcntl.lockf(lockfile,fcntl.LOCK_EX | fcntl.LOCK_NB)

        # open cdat, read the data
        data=read_cdat_data(cdatpath,field,timestep)

        # open idx and create query
        dataset,access,query=create_idx_query(idxpath,field,timestep,box,hz)

        # validate bounds
        if query.end() or data.size!=query.getNumberOfSamples().innerProduct():
            raise ConvertError(RESULT_ERROR,"Invalid IDX query.")
            
        # validate shape
        shape=data.shape[::-1]
        for i in range(len(shape)):
            if shape[i]!=query.getNumberOfSamples()[i]:
                raise ConvertError(RESULT_ERROR,"Invalid query dimensions.")
                
        # convert data
        visusarr=Visus.Array.fromNumPyArray(data)
        visusarrptr=Visus.ArrayPtr(visusarr)
        query.setBuffer(visusarrptr)
        ret=query.execute()
        if not ret:
            raise ConvertError(RESULT_ERROR,"Error executing IDX query.")
            
    except IOError as e:
        if e.errno==None:
            raise ConvertError(RESULT_ERROR,"Error reading data. Please ensure cdms2 is working and NetCDF data is accessible.")
        else:
            raise ConvertError(RESULT_BUSY,"Could not acquire lock file: conversion may already be in progress. Returning.")
    except cdms2.CDMSError as e:
        raise ConvertError(RESULT_ERROR,"CDMSError: %s"%e)
    except ConvertError as e:
        result=e.code
        result_str=e.msg
    except Exception as e:
        result=RESULT_ERROR
        result_str="unknown error occurred ("+str(e)+")"
    finally:
        lockfile.close()
        remove(lockfilename)

    interval=time.clock()-t1
    print('Total time %d msec.' % (interval*1000))

    return (result_str,result)



# ############################
if __name__ == '__main__':

    default_idx_db_path="/for_ganzberger1/idx/idx/idx.db"
    default_port=42299

    app=Visus.Application()
    app.setCommandLine("")
    app.useModule(Visus.IdxModule.getSingleton())  

    import argparse
    parser = argparse.ArgumentParser(description="Convert CDAT data to IDX format.")
    parser.add_argument("-p","--port"    ,default=default_port       ,help="listen on port")
    parser.add_argument("-d","--database",default=default_idx_db_path,help="cdat <--> idx database")
    args = parser.parse_args()

    global dbpath
    dbpath=args.database

    # start server
    httpd = SocketServer.ThreadingTCPServer(('localhost', args.port),cdatConverter)
    print "serving at port", args.port
    try:
        httpd.serve_forever()
    except:
        pass

    httpd.shutdown()
    print "done!"
