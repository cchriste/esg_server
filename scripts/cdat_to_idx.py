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
#from xml.dom import minidom
#import re
#import string
#import json
import visuspy as Visus
from copy import deepcopy

#****************************************************
# def read_xml(xml):

#     # read xml
#     doc = minidom.parse(xml)

#     # dataset
#     ds=doc.getElementsByTagName('dataset')[0]

#     # collect axes
#     axes = ds.getElementsByTagName("axis")

#     # collect variables
#     vars = ds.getElementsByTagName("variable")

#     # filemap
#     filemap = ds.getAttribute("cdms_filemap")

#     # huge pain to reconstruct this string to a list:
#     filemap = re.sub(r",([^,]*?\.nc)",",\"\g<1>\"",filemap)
#     filemap = re.sub(r"([\[,])([a-zA-Z0-9_]+)","\g<1>\"\g<2>\"",filemap)
#     filemap = re.sub(r"([\[,])-", "\g<1>null", filemap)
#     filemap = json.loads(filemap)

#     return (axes,vars,filemap)

#****************************************************
def create_idx(idxinfo):
    """Create a new idx volume from the information in idxinfo (fields, dims, timesteps)"""
    #import pdb; pdb.set_trace()

    idxfile=Visus.IdxFile()

    # set logical bounds
    rngmax=Visus.NdPoint()
    rngmax.x=1
    if len(idxinfo.dims) == 1:
        rngmax.x=idxinfo.dims[0]-1
    elif len(idxinfo.dims) == 2:
        rngmax.x=idxinfo.dims[0]-1
        rngmax.y=idxinfo.dims[1]-1
    elif len(idxinfo.dims) == 3:
        rngmax.x=idxinfo.dims[0]-1
        rngmax.y=idxinfo.dims[1]-1
        rngmax.z=idxinfo.dims[2]-1
    idxfile.logic_box=Visus.NdBox(Visus.NdPoint(),rngmax);

    # add fields
    for f in idxinfo.fields:
        idxfile.fields.push_back(f)

    # set timesteps
    if idxinfo.timesteps > 0:
        idxfile.timesteps.insert(0);
        idxfile.timesteps.insert(float(idxinfo.timesteps))
        idxfile.time_template="time%0"+str(len(str(idxinfo.timesteps)))+"d/"

    bSaved=idxfile.save(str(idxinfo.path))
    if not bSaved:
        print "ERROR creating idx "+ idxinfo.path


#****************************************************
def cdat_to_idx(cdat_filename,destpath):
    """Reads .nc or cdat .xml file and creates corresponding idx volumes, one per domain.
    In addition, it creates database tables to facilitate converting the actual data."""

    # create destination path
    idxbasename=os.path.splitext(os.path.basename(cdat_filename))[0]
    destpath+="/"+idxbasename
    try:
        os.mkdir(destpath)
    except:
        None

    #os.chdir(destpath)

    # open idx db
    #db = web.database(destpath+'/idx.db',dbn='sqlite',db='main')

    # insert new dataset into db
    #db_insert(db, 'datasets',idxbasename)
    #TODO: insert the rest

    # open dataset
    dataset = cdms2.open(cdat_filename)
    vars=dataset.variables
    #varnames=vars.keys()

    # Calculate range of value for logic_to_physic
    # We need to use <axis>_bnds var to get full
    # extents, which may not be accessible, so do our best.
    physical_bounds={}
    for axis in dataset.axes:
        if not hasattr(axis,'bounds'):
            continue
        try:
            B=dataset(axis.bounds)
            assert(len(B.shape)==2)  #bounds should be (len(arr_axis),2) where for each value of the arr axis there is a min and max
            physical_bounds[axis.id]=(B[0][0],B[-1][1])  #assume regular spacing
        except IOError:
            print "bounds not found, skipping",axis.bounds

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
                sz=len(dataset.axes[axes[i]])
                if axis=="time":
                    domains[axes].idxinfo.timesteps = sz
                else:
                    domains[axes].idxinfo.dims.append(sz)
                    if physical_bounds.has_key(axis):
                       rng=physical_bounds[axis][1]-physical_bounds[axis][0]
                       domains[axes].idxinfo.logic_to_physic[4*i+i]=float(sz)/float(rng)

            # fields            
            f=Visus.Field(v.id,Visus.DType(v.dtype.name))
            domains[axes].idxinfo.fields=[f]

    for d in domains.values():
        # print "creating idxfile for",d.id,"containing fields",d.varlist

        # create the idx
        create_idx(d.idxinfo)

        # insert into idx db: idx volumes indexed by variable
        #db_insert(d)

    return 0
        
#****************************************************

if __name__ == '__main__':
    if (len (sys.argv) < 3):
        print "usage: python cdat_to_idx.py <path_to_source_filename> <destination_basepath>"
        print "   ex: python cdat_to_idx.py /for_ganszberger1/xml/sample_dataset.xml /for_ganzberger1/idx"
        exit (1)
    app=Visus.Application()
    app.setCommandLine("")
    app.useModule(Visus.IdxModule.getSingleton())  
    cdat_filename = sys.argv[1]
    destpath = sys.argv[2]
    cdat_to_idx(cdat_filename,destpath)
