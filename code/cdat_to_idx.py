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
# cdat_to_idx.py
#
# 1) Constructs idx file(s) for the corresponding cdat (.xml or .nc) file.
# 2) Populates database backend to be used when on-the-fly data conversion is requested.
#
#
#****************************************************

import cdms2
import os
import sys
import sqlite3
import visuspy as Visus
from copy import deepcopy


#****************************************************
def getIdxPaths(cdat_dataset,db):
    """Looks in sqlite database db for idxfiles entries that refer to cdat_database. Returns a list of such entries."""
    ret=[]
    cur=db.cursor()
    cur.execute("SELECT ds_id from datasets where pathname=\"%s\"" % cdat_dataset)
    cdat_id=cur.fetchall()
    ds_id=-1
    assert(len(cdat_id)<=1)
    if len(cdat_id)>0:
        ds_id=cdat_id[0]
        cur.execute("SELECT * from idxfiles where ds_id=%d" % ds_id)
        idxfiles=cur.fetchall()
        for f in idxfiles:
            ret.append(f[1])

    return ret,ds_id

        
#****************************************************
def create_idx(idxinfo):
    """Create a new idx volume from the information in idxinfo (fields, dims, timesteps)"""

    idxfile=Visus.IdxFile()

    # set logical bounds
    idxfile.logic_box=Visus.NdBox()
    if len(idxinfo.dims) > 0:
        idxfile.logic_box.setP2(0,idxinfo.dims[0]);
    if len(idxinfo.dims) > 1:
        idxfile.logic_box.setP2(1,idxinfo.dims[1]);
    if len(idxinfo.dims) > 2:
        idxfile.logic_box.setP2(2,idxinfo.dims[2]);

    # set logic_to_physic
    m=idxinfo.logic_to_physic
    idxfile.logic_to_physic=Visus.Matrix(m[0],m[1],m[2],m[3],m[4],m[5],m[6],m[7],m[8],m[9],m[10],m[11],m[12],m[13],m[14],m[15]) #tgtbabw!

    # add fields
    for f in idxinfo.fields:
        idxfile.fields.push_back(f)

    # set timesteps
    if idxinfo.timesteps > 0:
        idxfile.timesteps.addTimesteps(0,idxinfo.timesteps-1,1);
        idxfile.time_template="time%0"+str(len(str(idxinfo.timesteps)))+"d/"

    bSaved=idxfile.save(str(idxinfo.path))
    if not bSaved:
        print "ERROR creating idx "+ idxinfo.path


#****************************************************
def cdat_to_idx(cdat_dataset,destpath,db,hostname,hostuser,hostpass,service):
    """Reads .nc or cdat .xml file and creates corresponding idx volumes, one per domain.
    In addition, it creates database tables to facilitate converting the actual data."""

    # create destination path
    idxbasename=os.path.splitext(os.path.basename(cdat_dataset))[0]
    try:
        os.mkdir(destpath)
    except:
        None  #directory likely already exists

    # open dataset
    dataset = cdms2.open(cdat_dataset)
    vars=dataset.variables

    # Calculate range of value for logic_to_physic
    # We need to use <axis>_bnds var to get full
    # extents, which may not be accessible, so do our best.
    physical_bounds={}
    for name in dataset.axes:
        axis=dataset.axes[name]
        if hasattr(axis,'bounds'):
            try:
                B=dataset(axis.bounds)
                assert(len(B.shape)==2)  #bounds should be (len(arr_axis),2) where for each value of the arr axis there is a min and max
                physical_bounds[name]=(B[0][0],B[-1][1])  #assume regular spacing
            except IOError:
                print "bounds not found, skipping",axis.bounds
        elif vars.has_key(name+"_bnds"):
            B=dataset(name+"_bnds")
            if len(B.shape)!=2:
                print "WARNING: bounds should be (len(arr_axis),2) where for each value of the arr axis there is a min and max"
                print "         B.shape =",str(B.shape)
            physical_bounds[name]=(B[0][0],B[-1][1])  #assume regular spacing

    # collect variables into their associated domains
    logic_to_physic=[1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
    field=type('field',(object,),{'name':None,'ndtype':1,'dtype':None})()  #cheap class-like defs
    idxinfo=type('idxinfo',(object,),{'cdat_dataset':None,'path':None,'fields':None,'dims':None,'logic_to_physic':None,'timesteps':0})()
    domain=type('domain',(object,),{'id':None,'shape':None,'idxinfo':None,'varlist':None})()
    domains={}
    for v in vars.values():
        v.id
        axes=tuple(v.getAxisIds()[::-1])
        if len(axes)==0:
            continue;
        axes

        if domains.has_key(axes):
            #print "inserting",v.id,"into existing entry of domains["+str(axes)+"]"
            domains[axes].varlist.append(v.id)
            f=Visus.Field(v.id,Visus.DType(v.dtype.name))
            f.default_layout="rowmajor"
            f.default_compression="zip"
            if hasattr(v,'long_name'):
                f.setDescription(v.long_name)
            domains[axes].idxinfo.fields.append(f)
            #print "domains["+str(axes)+"].varlist="+str(domains[axes].varlist)
        else:
            #print "inserting",v.id,"as NEW entry of domains["+str(axes)+"]"
            domains[axes]=deepcopy(domain)
            domains[axes].id=axes
            domains[axes].shape=v.shape[::-1]
            domains[axes].varlist=[v.id]
            #print "domains["+str(axes)+"].varlist="+str(domains[axes].varlist)
            domains[axes].idxinfo=deepcopy(idxinfo)
            domains[axes].idxinfo.cdat_dataset=idxbasename
        
            #idx name
            domains[axes].idxinfo.path=destpath+"/"+idxbasename+"-"
            for d in axes:
                domains[axes].idxinfo.path += d
                if d!=axes[-1]:
                    domains[axes].idxinfo.path += '_'
            domains[axes].idxinfo.path += ".idx"

            #dims,timesteps,logic_to_physic
            domains[axes].idxinfo.dims=[]
            domains[axes].idxinfo.logic_to_physic=logic_to_physic[:]
            for i in range(len(axes)):
                axis=axes[i]
                sz=len(dataset.axes[axes[i]])
                if axis.startswith("time"):  #note: some axes named time_<ntimesteps> (with opendap), others just named time
                    domains[axes].idxinfo.timesteps = sz
                else:
                    domains[axes].idxinfo.dims.append(sz)
                    if physical_bounds.has_key(axis):
                       rng=physical_bounds[axis][1]-physical_bounds[axis][0]
                       domains[axes].idxinfo.logic_to_physic[4*i+i]=float(sz)/float(rng)

            # fields            
            f=Visus.Field(v.id,Visus.DType(v.dtype.name))
            f.default_layout="rowmajor"
            f.default_compression="zip"
            if hasattr(v,'long_name'):
                f.setDescription(v.long_name)
            domains[axes].idxinfo.fields=[f]

    # insert new dataset into db
    cur=db.cursor()
    cur.execute("INSERT into datasets (pathname) values (\"%s\")" % cdat_dataset)
    cdat_id=cur.lastrowid

    for d in domains.values():
        found_time=False
        for axis in d.id:
            found_time |= axis.startswith("time")
        if len(d.id)<3 or len(d.id)>4 or not found_time:
            print "Skipping",d.id,"because it isn't a 2D or 3D field with time."
            continue

        print "creating idxfile for",d.id,"containing fields",d.varlist

        # create the idx
        create_idx(d.idxinfo)

        # insert into idx db
        cur.execute("INSERT into idxfiles (pathname, ds_id) values (\"%s\", %d)" % (os.path.basename(d.idxinfo.path), cdat_id))

        # register with server
        from urlparse import urlparse,urlunparse
        from urllib import quote
        import urllib2
        name=os.path.splitext(os.path.basename(d.idxinfo.path))[0]
        print hostname
        url=urlparse(hostname)
        url=url._replace(query="action=AddDataset&username="+hostuser+"&password="+hostpass+"&xml="+quote("<dataset name=\""+name+"\" permissions=\"public\" url=\"file://"+d.idxinfo.path+"\" ><access name=\"Multiplex\" type=\"multiplex\"><access chmod=\"r\" type=\"disk\" /><access chmod=\"r\" ondemand=\"external\" path=\""+service+"/convert\" type=\"ondemandaccess\" /><access chmod=\"r\" type=\"disk\" /></access></dataset>"))
        print url
        try:
            ret = urllib2.urlopen(urlunparse(url)).read()
            print ret
        except urllib2.HTTPError, e:
            print "HTTP error adding dataset to server: %d" % e.code
        except urllib2.URLError, e:
            print "Network error adding dataset to server: %s" % e.reason.args[1]        
        #except httplib.BadStatusLine, e:
            #print "BadStatusLine:",e
        except Exception,e:
            print "unknown exception:",e

#****************************************************
def make_visus_config(idx_paths,dataset,hostname):
    cfg="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<visus>\n"
    cfg+="  <group name=\""+os.path.splitext(os.path.basename(dataset))[0]+"\">\n"
    for path in idx_paths:
        dsname=os.path.splitext(os.path.basename(path))[0]
        cfg+="    <dataset name=\""+dsname+"\" url=\""+hostname+"?dataset="+dsname+"\" >\n"
        cfg+="      <access name=\"Multiplex\" type=\"multiplex\">\n"
        cfg+="        <access name=\"cache\"  type=\"disk\" chmod=\"rw\" url=\"$(VisusCacheDirectory)/"+dsname+"/visus.idx\" />\n"
        cfg+="        <access name=\"source\" type=\"network\" chmod=\"r\" compression=\"zip\" />\n"
        cfg+="      </access>\n"
        cfg+="    </dataset>\n"
    cfg+="  </group>\n</visus>\n"
    return cfg


#****************************************************
default_server="http://localhost:10000/mod_visus"
default_service="http://localhost:42299/convert"
default_username="root"
default_password="visus"

#****************************************************
def generate_idx(inputfile,outputdir,database=None,server=default_server,username=default_username,password=default_password,service=default_service,force=False):
    """return visus.config with address of idx volumes corresponding with given climate dataset.
    If idx volumes do not exist, they will be created and registered with the given server."""

    app=Visus.Application.getCurrent()
    if not app:
        app=Visus.Application()

    # open idx db
    if not database:
        database=outputdir+'/idx.db'
    db = sqlite3.connect(database)

    with db:
        inputfile=os.path.abspath(inputfile)
        outputdir=os.path.abspath(outputdir)
        idx_paths,ds_id=getIdxPaths(inputfile,db)

        # if force recreate, delete existing entries in database 
        if force:
            cur=db.cursor()
            cur.execute("DELETE from datasets where ds_id=%d"%ds_id)
            for path in idx_paths:
                cur.execute("DELETE from idxfiles where ds_id=%d"%ds_id)

        if len(idx_paths)==0 or force:
            cdat_to_idx(inputfile,outputdir,db,server,username,password,service)

            print "done creating idx volumes for",inputfile
            idx_paths,ds_id=getIdxPaths(inputfile,db)
        else:
            print "idx volumes already exist for",inputfile
            
        xml=make_visus_config(idx_paths,inputfile,server)

    db.close()
    return xml


#****************************************************
if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description="Create (empty) IDX volumes for all fields of given CDAT volume (.xml or .nc file).")
    parser.add_argument("-i","--inputfile",required=True,help="cdat volume to read")
    parser.add_argument("-o","--outputdir",required=True,help="basepath for idx volumes")
    parser.add_argument("-d","--database",required=False,help="path to idx<->cdat database")
    parser.add_argument("-s","--server",required=False,help="server with which volumes shoud be registered",default=default_server)
    parser.add_argument("-u","--username",required=False,help="username for registering with server",default=default_username)
    parser.add_argument("-p","--password",required=False,help="password for registering with server",default=default_password)
    parser.add_argument("-v","--service",required=False,help="on-demand climate data converter service address",default=default_service)
    parser.add_argument("-f","--force",action="store_true",dest="force",required=False,default=False,help="force creation even if idx volumes already exist")
    args = parser.parse_args()

    xml=generate_idx(args.inputfile,args.outputdir,args.database,args.server,args.username,args.password,args.service,args.force)
    print xml

