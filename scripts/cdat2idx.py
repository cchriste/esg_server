#!/usr/bin/python

#***************************************************
#** ViSUS Visualization Project                    **
#** Copyright (c) 2010 University of Utah          **
#** Scientific Computing and Imaging Institute     **
#** 72 S Central Campus Drive, Room 3750           **
#** Salt Lake City, UT 84112                       **
#**                                                **
#** For information about this project see:        **
#** http://www.pascucci.org/visus/                 **
#**                                                **
#**      or contact: pascucci@sci.utah.edu         **
#**                                                **
#****************************************************

#
# To run this example, you will need to build and install the visuspy
# swig module (configure ViSUS with ENABLE_SWIG, see
# <nvisusio>/README.txt for details) and also the uv-cdat package (see
# instructions at http://uv-cdat.llnl.gov/wiki/VistrailsBuild).
#
# you must 'export PYTHONPATH=/path/to/cdms2/installation'
#

from visuspy import *
import sys,os
import cdms2

dirstack=[]
def pushd(dirname):
  dirstack.append(os.getcwd())
  os.chdir(dirname)

def popd():
  os.chdir(dirstack.pop())

###############################################################################
def createFileList(basename):
  # Create an ordered list of files from template_filename which may contain unix shell-style expansions (*, ?, []).
  import glob
  filelist=glob.glob(basename)
  filelist.sort()
  return filelist

###############################################################################
class CDATConverter:

  def __init__(self,basedir,institution,model,experiment,frequency,domain,runs,variables,outdir,compressed):
    self.basedir=basedir
    self.institution=institution
    self.model=model
    self.experiment=experiment
    self.frequency=frequency
    self.domain=domain
    self.runs=runs
    self.variables=variables
    self.outdir=outdir
    self.compressed=compressed

    if self.domain != "atmos":
      print "need to handle other domains with domain frequencies other than Amon"
      fail()

  #listVarTypes
  def getVars(self):
    varspath=self.basedir+"/"+self.institution+"/"+self.model+"/"+self.experiment+"/"+self.frequency+"/"+self.domain+"/"+"Amon"+"/"+runs[0]
    pushd(varspath)
    shapes=[]   # for each item in shapes (a set of dims), there is a list of vars in varlist
    varlist=[]
    for varname in self.variables:
      varpath=varspath+"/"+varname+"/1"
      ncfiles=os.listdir(varpath)
      for ncfile in ncfiles:
        #print varname, ncfile
      
        # This gets us a special file handle
        f = cdms2.open(varpath+"/"+ncfile)

        # For demonstration purposes let's extract the field name which is
        # typically the last variable. In practice this can be gotten from the
        # directory names for example
        #var_name = file.getVariables()[-1].id

        #print "variables:",f.listvariable()
        #print "dimensions:",f.listdimension()
        #print "globals:",f.listglobal()

        #print "f.showAll(v):",f.showall(varname)

        # This gets us a handle to the data but not the data itself.
        v = f(varname)
        #v = f(varname,time=...,squeeze=1) #reduce spurious dimensions... deletes dimensions of length 1

        #print varname
        #import pdb; pdb.set_trace()
        #print "\tdtype:",v.dtype
        #print "\tshape:",v.shape
        #print "\time:",v.getTime()
        #print "\tlong_name:",v.long_name

        shape=v[0].shape
        varlist_id=-1
        for s in xrange(len(shapes)):
          if shapes[s] == shape:
            varlist_id=s
            break
        if varlist_id==-1:
          shapes.append(shape)
          varlist.append(dict())
          varlist_id=len(shapes)-1
        flags=""
        if self.compressed:
          flags+="compressed"
        DTYPE=DType.New(v.dtype.name)
        NDTYPE=1
        varstr=varname+" %d*%s %s" % (NDTYPE,DType.toString(DTYPE),flags)
        #print varlist_id, varname
        varlist[varlist_id][varname]=(varstr,ncfiles)

        #print "v:",v

        #print "datatype:",v.datatype

        #print "v shape:",v.shape

        #print "v info:",v.info()

        # Lets get the time axis
        #time = v.getTime()
        #print "Found data for time:\n", time

        # And convert it into human readable format
        #time = time.asComponentTime()

        # And look at the dimension and axis of the data
        #shape = v.shape
        #lat = v.getLatitude()
        #lon = v.getLongitude()
        #print "Spatial resolution is ", shape[1:], " covering [%f,%f] x [%f,%f]\n" % (lat[0],lat[-1],lon[0],lon[-1])

        #print len(time),"timesteps"
        #print len(v),"vs"

        #hdbuf=numpy.ravel(v[0])
        #buf=numpy.append(buf,hdbuf)                        #so instad just use append

        # Now we could convert "all" the data 
        # for t,data in zip(time,v[0:10]):

        #   # Convert the time into some sane reference system
        #   day = t.torel('days since 1850-01-01')

        #   print day,":  ",data.data.__class__

    popd()
    return shapes,varlist

  # createIdx
  def createIdxVolumes(self,shapes,varlist):
    # Create IDX volumes based on shapes and varlist. Determines
    # resolution of volumes based on shapes and adds corresponding
    # fields in varlist to each shape.

    if len(shapes)==0 or len(shapes)!=len(varlist):
      return

    print "creating idx volumes at",self.outdir,"for:",shapes,varlist
    for run in runs:
      varspath=self.basedir+"/"+self.institution+"/"+self.model+"/"+self.experiment+"/"+self.frequency+"/"+self.domain+"/"+"Amon"+"/"+run
      for s,shape in enumerate(shapes):
        userbox     =NdBox()
        userbox.From=NdPoint(0,0,0)
        suffix=""
        if len(shape)==1:
          userbox.To  =NdPoint(shape[0])
          suffix="_1d"
        elif len(shape)==2:
          userbox.To  =NdPoint(shape[0],shape[1])
          suffix="_2d"
        else:
          userbox.To  =NdPoint(shape[0],shape[1],shape[2])
          suffix="_3d"
        bitsperblock=0        # Automatically determine bitmask and bitsperblock
        bitmask_pattern=""
        fieldstr=""
        for k in varlist[s].keys():
          fieldstr+=varlist[s][k][0]+"+"
        outdir=self.outdir+"/"+self.institution+"/"+self.model+"/"+self.frequency+"/"+run+suffix+".idx"
        vf=IdxDataset.New(outdir,run,userbox,fieldstr[:-1],bitmask_pattern,bitsperblock)
        assert(vf)
        access=vf.createAccess()

        #write fields
        for k in varlist[s].keys():
          ncfiles=varlist[s][k][1]
          field=vf.getField(k)
          for ncfile in ncfiles:
            ncfile=ncfile.replace(self.runs[0],run)
            print "opening",ncfile,"for writing..."
            f = cdms2.open(varspath+"/"+k+"/1/"+ncfile)
            v = f(k)
            for t in xrange(len(v)):
              buf=numpy.ravel(v[t])
              print "for time",t,"buflen=",len(buf)
              write=vf.createBoxQuery(userbox,field,t)
              assert(write)
              #write.setBuffer(MemoryBlock(buf))
              DTYPE=DType.New(v.dtype.name)
              write.data=PArray([len(buf)],DTYPE,buf)
              retval=write.execute(access,ord('w'))
              print "write returned",retval
              assert(retval==QuerySucceed)


  def foo(self):
    #old createIdx method from hdf2idx

    nslices_per_write=256 # faster to write a group of slices all at once if you have sufficient memory
    
    # Open the first file to determine dimensions of the volume.
    zdim=len(filelist)
    fd=SD.SD(filelist[0]).select(0)
    xdim,ydim=fd.dimensions().values()
    hdbuf=fd.get()
    DTYPE=DType.New(hdbuf.dtype.name)
    NDTYPE=1
    buf=numpy.array(numpy.zeros((0,),dtype=hdbuf.dtype))
    print "dimensions: %d x %d x %d" % (xdim,ydim,zdim)

    # Create the IDX volume
    userbox=NdBox()
    userbox.From=NdPoint(0,0,0)
    userbox.To  =NdPoint(xdim-1,ydim-1,zdim-1)
    flags="compressed"
    fields="data %d*%s %s" % (NDTYPE,DType.toString(DTYPE),flags)
    bitsperblock=0        # Automatically determine bitmask and bitsperblock
    bitmask_pattern=""
    vf=IdxDataset.New(idxname,idxdata,userbox,fields,bitmask_pattern,bitsperblock)
    assert(vf)
    field=vf.getField()
    time=vf.getTimeFrom()
    access=vf.createAccess()

    # Write all the files nslices at a time.
    slicenum=0
    startslice=0
    for I in range(0,len(filelist)):
      slicenum=slicenum+1

      # Open the file
      print "reading",filelist[I],"..."
      fd=SD.SD(filelist[I]).select(0)
      
      # Verify dimensions
      fxdim,fydim=fd.dimensions().values()
      assert(fxdim==xdim and fydim==ydim)

      # Copy the data to Visus MemoryBlock
      hdbuf=numpy.ravel(fd.get())
      #numpy.copyto(buf[xdim*ydim*(slicenum-1)],hdbuf)   #not sure how to reference internal array location for dst (1st argument)
      buf=numpy.append(buf,hdbuf)                        #so instad just use append
#(very slow way to do the same thing)
#      for i in range(0,ydim):
#        for j in range(0,xdim):
#          buf[(slicenum-1)*ydim*xdim+i*xdim+j]=hdbuf[i][j]

      if slicenum==nslices_per_write:
        # Create the IDX query
        userbox.From.z=startslice
        userbox.To.z=startslice+slicenum-1
        print "writing slices",userbox.From.z,"through",userbox.To.z
        write=vf.createIdxBoxQuery(userbox,field,time,0,vf.maxh,vf.maxh)
        assert(write)
        write.setBuffer(MemoryBlock(buf))
        retval=write.execute(access,ord('w'))
        assert(retval==QueryFinished)
        startslice=startslice+slicenum
        slicenum=0

    #write remainder
    if slicenum>0:
      # Create the IDX query
      userbox.From.z=startslice
      userbox.To.z=startslice+slicenum-1
      print "writing slices",userbox.From.z,"through",userbox.To.z,"(remainder)"
      write=vf.createIdxBoxQuery(userbox,field,time,0,vf.maxh,vf.maxh)
      assert(write)
      write.setBuffer(MemoryBlock(buf))
      retval=write.execute(access,ord('w'))
      assert(retval==QueryFinished)

    print "done!"

    
def fail():
  print "exiting..."
  popd()

    
# ############################
if __name__ == '__main__':
  cdat_basedir="/usr/sci/cedmav/data/climate/cmip5"
  pushd(cdat_basedir)
  outdir="/usr/sci/cedmav/data/climate/idx"

  import argparse

  parser = argparse.ArgumentParser(description="Convert CDAT data to IDX format. Expects input of the form {Institution}/{Model}/{experiment}/{frequency}/{domain}/{$$$}/{run-id}/{variable}/{???}/{filename(s).nc}")
  parser.add_argument("-n", "--nothing", action="store_true", dest="innocuous", 
                    default=False,
                    help="dry-run: does not perform any permanent action")
  parser.add_argument("-i","--institution")
  parser.add_argument("-m","--model")
  parser.add_argument("-e","--experiment",default="historical",help="(default: %(default)s)")
  parser.add_argument("-f","--frequency",default="mon",help="(default: %(default)s)")
  parser.add_argument("-d","--domain",default="atmos",help="(default: %(default)s)")
  parser.add_argument("-r","--run",type=int,help="(blank: all runs)")
  parser.add_argument("-v","--variables",nargs="*",help="(blank: all variables)")
  parser.add_argument("-o","--output",default=outdir,help="utput directory (default: %(default)s)")
  parser.add_argument("-c","--compressed",action="store_true",default=False)
  args = parser.parse_args()

  if not args.institution:
    print "institution is required, options are:",os.listdir(".")
  elif not args.model:
    print "model is required, options are:",os.listdir("./"+args.institution)
  elif not args.experiment:
    print "experiment is required, options are:",os.listdir("./"+args.institution+"/"+args.model)
  elif not args.frequency:
    print "frequency is required, options are:",os.listdir("./"+args.institution+"/"+args.model+"/"+args.experiment)
  elif not args.domain:
    print "domain is required, options are:",os.listdir("./"+args.institution+"/"+args.model+"/"+args.experiment+"/"+args.frequency)
  else:
    allruns=sorted(os.listdir("./"+args.institution+"/"+args.model+"/"+args.experiment+"/"+args.frequency+"/"+args.domain+"/Amon"))
    if args.run==None:
      runs=allruns;
    else:
      if args.run>=len(allruns):
        print "run must be in range [ 0,",len(allruns),"]"
        fail()
      runs=[allruns[args.run]]

    print "institution:",args.institution
    print "model:",args.model
    print "experiment:",args.experiment
    print "frequency:",args.frequency
    print "domain:",args.domain
    print "runs:",runs
    if not args.variables:
      variables=os.listdir("./"+args.institution+"/"+args.model+"/"+args.experiment+"/"+args.frequency+"/"+args.domain+"/Amon/"+runs[0])
    else:
      variables=args.variables
    print "variables:",variables
    print "compressed:",args.compressed

    cdat=CDATConverter(cdat_basedir,args.institution,args.model,args.experiment,args.frequency,args.domain,runs,variables,args.output,args.compressed)
    (shapes,varlist)=cdat.getVars()
    #print "shapes:",shapes
    #print "varlist:",varlist
      
    # initialize ViSUS
    app=Application();app.setCommandLine("_visuspy.pyd")
    ENABLE_VISUS_IDX()  

    #create volumes
    cdat.createIdxVolumes(shapes,varlist)

  fail()


