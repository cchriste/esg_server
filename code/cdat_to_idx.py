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
import VisusIdxPy
from copy import deepcopy
from lxml import etree
import urllib2
import base64
from urlparse import urlparse,urlunparse
from urllib import quote

import numpy
import XidxPy
from XidxPy import *

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
def validatePaths(paths,basedir):
    """Verifies the given paths exist."""
    ret=True
    for path in paths:
        ret &= os.path.isfile(basedir+'/'+path)
    return ret

#****************************************************
def create_midx(cdat_dataset,destpath,idxinfo):
    """Create a new midx file that contains path to idx file and the matrices that describe the volume"""
    root=etree.Element("dataset",typename="IdxMultipleDataset")

    name=os.path.splitext(os.path.basename(idxinfo.path))[0]
    child=etree.SubElement(root,"dataset",url="file://"+idxinfo.path,name=name)
    val = ""
    for m in idxinfo.logic_to_physic:
    	val+=str(m)+" "

    M=etree.SubElement(child,"M",value=val)
    tree=etree.ElementTree(root)
    
    idxbasename=os.path.splitext(os.path.basename(idxinfo.path))[0]
    filename=destpath+"/"+idxbasename+'.midx'
    tree.write(filename,pretty_print=True,xml_declaration=False,encoding="utf-8")
        
#****************************************************
def create_idx(idxinfo):
    """Create a new idx volume from the information in idxinfo (fields, dims, timesteps)"""
    dims = [0]*3
    if len(idxinfo.dims) > 0:
        dims[0] = idxinfo.dims[0];
    if len(idxinfo.dims) > 1:
        dims[1] = idxinfo.dims[1];
    if len(idxinfo.dims) > 2:
        dims[2] = idxinfo.dims[2];

    # temporary fix for 2D datasets
    if dims[2] == 0:
        dims[2] = 1
        
    # Set logical bounds
    dataset_logicbox = Visus.NdBox(Visus.NdPoint(0, 0, 0), Visus.NdPoint.one(dims[0], dims[1], dims[2]))
    idxfile = VisusIdxPy.IdxFile()
    idxfile.box = Visus.NdBox(dataset_logicbox)

    # add fields
    for f in idxinfo.fields:
        idxfile.fields.push_back(f)

    # set timesteps
    if idxinfo.timesteps > 0:
        idxfile.timesteps.addTimesteps(0, idxinfo.timesteps-1,1);
        idxfile.time_template="time%0"+str(len(str(idxinfo.timesteps)))+"d/"

    bSaved = idxfile.save(str(idxinfo.path))
    if not bSaved:
        print "ERROR creating idx "+ idxinfo.path


#****************************************************
def cdat_to_idx(cdat_dataset,destpath,db):
    """Reads .nc or cdat .xml file and creates corresponding idx volumes, one per domain.
    In addition, it creates database tables to facilitate converting the actual data."""

    # create destination path
    idxbasename=os.path.splitext(os.path.basename(cdat_dataset))[0]
    try:
        os.mkdir(destpath)
    except:
        None  #directory likely already exists

    print "destination", destpath

    ## XIDX init start

    # create time group
    time_group = Group("TimeSeries", Group.TEMPORAL_GROUP_TYPE)

    # create a list domain for the temporal group
    time_dom = ListDomainDouble("Time")

    # XIDX set group time domain
    time_group.SetDomain(time_dom)
 
    # create grid domain
    geo_dom = MultiAxisDomain("Geospatial")

    # group of variables sharing this domain
    geo_vars = Group("geo_vars", Group.SPATIAL_GROUP_TYPE, geo_dom);
    
    ## XIDX init end
    
    # open dataset
    print "cdat_to_idx: datasets="+cdat_dataset
    dataset = cdms2.open(cdat_dataset)
    vars=dataset.variables
    print "vars: "+str(vars)

    # Calculate range of value for logic_to_physic
    # We need to use <axis>_bnds var to get full
    # extents, which may not be accessible, so do our best.
    physical_bounds={}
    for name in dataset.axes:
        print "considering axis: "+name
        axis=dataset.axes[name]

        ## XIDX create axis start
        attributes = axis.attributes

        # use time axis for time domain
        # or create new axis for others
        if not name=="time":
          new_axis = Variable(name);
            
        for att in attributes:
          if att=="bounds":
            B=dataset(axis.bounds)
            shape=B.shape
            #print shape
            for i in range(shape[0]):
                entry=[]
                for j in range(shape[1]):
                  entry.append(B[i][j])
                if name=="time":
                  time_dom.AddDomainItems(IndexSpace(entry))
                else:
                  new_axis.AddValues(IndexSpace(entry))
          else:
            values=attributes[att]
            if isinstance(values, numpy.ndarray):
              values=numpy.array2string(attributes[att])
            #print att, attributes[att], type(attributes[att]), type(values)
            if attributes[att] and name=="time":
              time_dom.AddAttribute(att,attributes[att])
            else:
              new_axis.AddAttribute(att,values)
        
        if not name=="time":
          geo_dom.AddAxis(new_axis)  

        ## XIDX create axis end
        
        if hasattr(axis,'bounds'):
            try:
                B=dataset(axis.bounds)
                assert(len(B.shape)==2)  #bounds should be (len(arr_axis),2) where for each value of the arr axis there is a min and max
                physical_bounds[name]=(B[0][0],B[-1][1])  #assume regular spacing
            except IOError:
                print "bounds not found, skipping",str(axis.bounds)
        elif vars.has_key(name+"_bnds"):
            B=dataset(name+"_bnds")
            if len(B.shape)!=2:
                print "WARNING: bounds should be (len(arr_axis),2) where for each value of the arr axis there is a min and max"
                print "         B.shape =",str(B.shape)
            physical_bounds[name]=(B[0][0],B[-1][1])  #assume regular spacing

            
    # XIDX add geometric domain
    time_group.AddGroup(geo_vars);
    
    # collect variables into their associated domains
    print "finished considering axes"
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

        ## XIDX add variables start
        if not v.id.endswith("_bnds"): 
          # create and add a variable to the group
          temp = geo_vars.AddVariable(v.id, Visus.DType.fromString(v.dtype.name).toString());
          #print "var", v.id, "type", v.dtype.name
          attributes=v.attributes
          for att in attributes:
            values=attributes[att]
            if isinstance(values, numpy.ndarray):
              values=numpy.array2string(attributes[att])
            #print att, attributes[att], type(attributes[att]), type(values)
            if len(values)>0: #attributes[att]:
              temp.AddAttribute(att,values)
        ## XIDX add variables end
        
        if domains.has_key(axes):
            print "inserting",v.id,"into existing entry of domains["+str(axes)+"]"
            domains[axes].varlist.append(v.id)
            f=Visus.Field(v.id,Visus.DType.fromString(v.dtype.name))
            f.default_layout="rowmajor"
            #f.default_compression="zip"
            if hasattr(v,'long_name'):
                f.setDescription(v.long_name)
            domains[axes].idxinfo.fields.append(f)
            print "domains["+str(axes)+"].varlist="+str(domains[axes].varlist)
        else:
            print "inserting",v.id,"as NEW entry of domains["+str(axes)+"]"
            domains[axes]=deepcopy(domain)
            domains[axes].id=axes
            domains[axes].shape=v.shape[::-1]
            domains[axes].varlist=[v.id]
            print "domains["+str(axes)+"].varlist="+str(domains[axes].varlist)
            domains[axes].idxinfo=deepcopy(idxinfo)
            domains[axes].idxinfo.cdat_dataset=idxbasename
        
            #idx name
            domains[axes].idxinfo.path=destpath+"/"+idxbasename+".idx"#"-"
            # using axis to create the dataset path
            # for d in axes:
            #     domains[axes].idxinfo.path += d
            #     if d!=axes[-1]:
            #         domains[axes].idxinfo.path += '_'
            # domains[axes].idxinfo.path += ".idx"

            #dims,timesteps,logic_to_physic
            domains[axes].idxinfo.dims=[]
            domains[axes].idxinfo.logic_to_physic=logic_to_physic[:]
            for i in range(len(axes)):
                #import pdb;pdb.set_trace()
                axis=axes[i]
                sz=len(dataset.axes[axes[i]])
                if axis.startswith("time"):  #note: some axes named time_<ntimesteps> (with opendap), others just named time
                    domains[axes].idxinfo.timesteps = sz
                else:
                    print "appending sz"
                    domains[axes].idxinfo.dims.append(sz)
                    rng=1
                    if physical_bounds.has_key(axis):
                       rng=float(physical_bounds[axis][1]-physical_bounds[axis][0])/float(sz)
                    if not rng:              #note: assume longitude [0,360] and latitude [0,180] if not explicitly specified
                        if axis.startswith("lon"):
                            rng=float(360)/float(sz)
                        elif axis.startswith("lat"):
                            rng=float(180)/float(sz)
                    domains[axes].idxinfo.logic_to_physic[4*i+i]=rng

            # fields            
            f=Visus.Field(v.id,Visus.DType.fromString(v.dtype.name))
            f.default_layout="rowmajor"
            #f.default_compression="zip"
            if hasattr(v,'long_name'):
                f.setDescription(v.long_name)
            domains[axes].idxinfo.fields=[f]

    # insert new dataset into db
    print "inserting into db..."
    cur=db.cursor()
    cur.execute("INSERT into datasets (pathname) values (\"%s\")" % cdat_dataset)
    cdat_id=cur.lastrowid

    xidxpath = destpath+"/test.xidx"

    for d in domains.values():
        found_time=False
        print d
        for axis in d.id:
            found_time |= axis.startswith("time")
        if len(d.id)<3 or len(d.id)>4 or not found_time:
            print "Skipping",d.id,"because it isn't a 2D or 3D field with time."
            continue

        print "creating idxfile for",d.id,"containing fields",d.varlist

        # create the idx
        create_idx(d.idxinfo)
        # create the midx that contains path to idx file and logic_to_physic
        create_midx(cdat_dataset,destpath,d.idxinfo)
        # insert into idx db
        # since we add path to .midx into visus config, we will get the path to .midx in query string
        # therefore add path to .midx also into idx db
        idx=os.path.basename(d.idxinfo.path) 
        midx=os.path.splitext(idx)[0]+'.midx'
        # XIDX path assuming only one dataset per IDX file
        xidxpath=destpath+"/"+os.path.splitext(idx)[0]+'.xidx'
        cur.execute("INSERT into midxfiles (pathname, ds_id) values (\"%s\", %d)" % (midx, cdat_id))
        cur.execute("INSERT into idxfiles (pathname, ds_id) values (\"%s\", %d)" % (idx, cdat_id))

        # XIDX set data source to the dataset file
        source = DataSource("data", idx)
        time_group.AddDataSource(source)

    # create metadata file
    meta = XidxFile(xidxpath)

    # XIDX write metadata to disk             
    meta.SetRootGroup(time_group);
    meta.Save();

    print "xidx created"
   
    return domains

def send_url(url):
    """ sendurl using urllib2 """
    try:
        request = urllib2.Request(urlunparse(url))
        base64string = base64.encodestring('%s:%s' % ('visus', 'P@ssw0rd!')).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        ret = urllib2.urlopen(request).read()
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
def register_datasets(idx_paths,outputdir,hostname,service):
    """ register datasets with ViSUS data server """
    print "Ensuring new datasets are registered with ViSUS data server"

    for idx_path in idx_paths:
        dataset_name=os.path.splitext(os.path.basename(idx_path))[0]
        midx_path=os.path.splitext(idx_path)[0]+'.midx'
        # need to add both idx and midx to config becuase webviewer uses idx and visus viewer uses midx
        p = [idx_path, midx_path]
        n = [dataset_name+"_idx", dataset_name]
        print hostname
        for path, name in zip(p, n):
            url=urlparse(hostname)
            xml="<dataset name=\""+name+"\" permissions=\"public\" url=\"file://"+outputdir+'/'+path+"\" ><access name=\"Multiplex\" type=\"multiplex\"><access chmod=\"r\" type=\"disk\" /><access chmod=\"r\" ondemand=\"external\" path=\""+service+"/convert\" type=\"ondemandaccess\" /><access chmod=\"r\" type=\"disk\" /></access></dataset>"
            url=url._replace(query="action=AddDataset&xml="+quote(xml))
            print urlunparse(url)
            send_url(url)
        

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

#****************************************************
def generate_idx(inputfile,outputdir,database=None,server=default_server,service=default_service,force=False):
    """return visus.config with address of idx volumes corresponding with given climate dataset.
    If idx volumes do not exist, they will be created and registered with the given server."""

    VisusIdxPy.IdxModule.attach()

    # open idx db
    if not database:
        database=outputdir+'/idx.db'
    db = sqlite3.connect(database)

    with db:
        inputfile=os.path.abspath(inputfile)
        outputdir=os.path.abspath(outputdir)
        idx_paths,ds_id=getIdxPaths(inputfile,db)

        if not validatePaths(idx_paths,outputdir):
            print "idx files do not exist: (re)creating them"
            force=True

        # if force recreate, delete existing entries in database 
        if force:
            cur=db.cursor()
            cur.execute("DELETE from datasets where ds_id=%d"%ds_id[0])
            for path in idx_paths:
                cur.execute("DELETE from idxfiles where ds_id=%d"%ds_id[0])
                cur.execute("DELETE from midxfiles where ds_id=%d"%ds_id[0])

        if len(idx_paths)==0 or force:
            cdat_to_idx(inputfile,outputdir,db)

            print "done creating idx volumes for",inputfile
            idx_paths,ds_id=getIdxPaths(inputfile,db)
        else:
            print "idx volumes already exist for",inputfile
            
        register_datasets(idx_paths,outputdir,server,service)
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
    parser.add_argument("-v","--service",required=False,help="on-demand climate data converter service address",default=default_service)
    parser.add_argument("-f","--force",action="store_true",dest="force",required=False,default=False,help="force creation even if idx volumes already exist")
    args = parser.parse_args()

    xml=generate_idx(args.inputfile,args.outputdir,args.database,args.server,args.service,args.force)
    print xml

