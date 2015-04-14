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
# xml_to_idx.py
#
# 1) Constructs idx file(s) corresponding to data described by xml file.
# 2) Populates database backend to be used when on-the-fly data conversion is requested.
#
#
#****************************************************

from xml.dom import minidom
import sys
import re
import string
import json
import os
import visuspy
import pdb

#****************************************************
def read_xml(xml):

    # read xml
    doc = minidom.parse(xml)

    # dataset
    ds=doc.getElementsByTagName('dataset')[0]

    # collect axes
    axes = ds.getElementsByTagName("axis")

    # collect variables
    vars = ds.getElementsByTagName("variable")

    # filemap
    filemap = ds.getAttribute("cdms_filemap")

    # huge pain to reconstruct this string to a list:
    filemap = re.sub(r",([^,]*?\.nc)",",\"\g<1>\"",filemap)
    filemap = re.sub(r"([\[,])([a-zA-Z0-9_]+)","\g<1>\"\g<2>\"",filemap)
    filemap = re.sub(r"([\[,])-", "\g<1>null", filemap)
    filemap = json.loads(filemap)

    return (axes,vars,filemap)

#****************************************************
def create_idx(idxinfo):

    pdb.set_trace()

    idxfile=visuspy.IdxFile()

    # set logical bounds
    rngmax=visuspy.NdPoint()
    rngmax.x=1
    if len(idxinfo['logical']) == 1:
        rngmax.x=idxinfo['logical'][0]-1
    elif len(idxinfo['logical']) == 2:
        rngmax.x=idxinfo['logical'][0]-1
        rngmax.y=idxinfo['logical'][1]-1
    elif len(idxinfo['logical']) == 3:
        rngmax.x=idxinfo['logical'][0]-1
        rngmax.y=idxinfo['logical'][1]-1
        rngmax.z=idxinfo['logical'][2]-1
    idxfile.logic_box=visuspy.NdBox(visuspy.NdPoint(),rngmax);

    # add fields
    for f in idxinfo['vars']:
        field=visuspy.Field(str(f[0]),visuspy.DType(f[1]))
        idxfile.fields.push_back(field)

    # set timesteps
    if idxinfo['timesteps'] > 0:
        idxfile.timesteps.insert(0);
        idxfile.timesteps.insert(float(idxinfo['timesteps']))
        idxfile.time_template="time%0"+str(len(str(idxinfo['timesteps'])))+"d/"

    bSaved=idxfile.save(str(idxinfo['name']))
    if not bSaved:
        print "ERROR creating idx "+ idxinfo['name']


#****************************************************
def xml_to_idx(xml,idx):

    # create destination path
    os.mkdir(idx)
    os.chdir(idx)

    # open idx db
    db = web.database('./idx.db',dbn='sqlite',db='main')

    # insert new dataset into db
    db_insert(db, 'datasets',os.path.splitext(os.path.basename(xml))[0])
    <ctc> gotta figure this out now

    # read xml
    (axes,vars,filemap) = read_xml(xml);

    # varnames
    varnames=[]
    for v in vars:
        varnames.append(v.getAttribute("id"))

    # domains
    domains={}
    for v in vars:
        D=v.getElementsByTagName("domain")[0].getElementsByTagName("domElem")
        domain=[]
        for d in D:
            domain.append(d.getAttribute("name"))
        domain=tuple(domain)
        if domains.has_key(domain):
            domains[domain].append(v.getAttribute("id"))
        else:
            domains[domain]=[v.getAttribute("id")]

    # construct idxinfo for each domain
    idxinfo={}
    for k in domains.keys():
        idxinfo[k]={}
        D = list(k);
        D.reverse()
        V = domains[k]

        # create idx name
        idxname=os.path.basename(idx)
        idxinfo[k]['name']=idx+"/"+idxname
        for d in D:
            idxinfo[k]['name'] += "_" + d
        idxinfo[k]['name'] += ".idx"
        
        # construct map from domain keys to logical extents
        timesteps = 0
        logical = []
        for d in D:
            for a in axes:
                if a.getAttribute("id") == d:
                    if "time" in d:
                        timesteps = a.getAttribute("length")
                    else:
                        logical.append(int(float(a.getAttribute("length"))))
                    # calculate range of value for logic_to_physic
                    # todo: need to use axis_bnds to get full extents
                    # vals = string.split(a.lastChild.nodeValue)[1:-1]
                    # for i in xrange(len(vals)):
                    #     vals[i] = float(vals[i])

        idxinfo[k]['logical'] = logical
        idxinfo[k]['timesteps'] = timesteps
        
        # determine type of vars
        idxinfo[k]['vars']=[]
        for v in V:
            for a in vars:
                if a.getAttribute("id") == v:
                    dt = a.getAttribute("datatype")
                    if dt == "Double":
                        idxinfo[k]['vars'].append((v, "1*float64"));
                    elif dt == "Float":
                        idxinfo[k]['vars'].append((v, "1*float32"));
                    else:
                        print "ERROR: unhandled variable type "+dt
                        return -1

        # create the idx
        create_idx(idxinfo[k])

        # insert into idx db
        db_insert(idxinfo[k])

    return 0

        
#****************************************************

if __name__ == '__main__':
    if (len (sys.argv) < 3):
        print "usage: python xml_to_idx.py <path_to_source_xml> <path_to_dest_idx>"
        print "   ex: python xml_to_idx.py /for_ganszberger1/idx/xml/sample_dataset.xml /for_ganzberger1/idx/idx/sample_dataset"
        exit (1)
    app=visuspy.Application()
    app.setCommandLine("")
    app.useModule(visuspy.IdxModule.getSingleton())  
    xml = sys.argv[1]
    idx = sys.argv[2]
    xml_to_idx(xml,idx)
