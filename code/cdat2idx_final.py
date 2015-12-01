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

###############################################################################
#dirstack
###############################################################################
dirstack=[]
def pushd(dirname):
  dirstack.append(os.getcwd())
  os.chdir(dirname)
def popd():
  os.chdir(dirstack.pop())

class Callable:
    """Callable, see http://code.activestate.com/recipes/52304-static-methods-aka-class-methods-in-python/"""
    def __init__(self,anycallable):
        self.__call__=anycallable

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

    if not self.institution:
      print "institution is required, options are:",os.listdir(".")
      exitprog("invalid institution")
    elif not self.model:
      print "model is required, options are:",os.listdir("./"+self.institution)
      exitprog("invalid model")
    elif not self.experiment:
      print "experiment is required, options are:",os.listdir("./"+self.institution+"/"+self.model)
      exitprog("invalid experiment")
    elif not self.frequency:
      print "frequency is required, options are:",os.listdir("./"+self.institution+"/"+self.model+"/"+self.experiment)
      exitprog("invalid frequency")
    elif not self.domain:
      print "domain is required, options are:",os.listdir("./"+self.institution+"/"+self.model+"/"+self.experiment+"/"+self.frequency)
      exitprog("invalid domain")

    amonpath=self.basedir+"/"+self.institution+"/"+self.model+"/"+self.experiment+"/"+self.frequency+"/"+self.domain
    self.runspath=CDATConverter.getRunsPath(amonpath)
    if not os.access(self.runspath,os.R_OK):
      exitprog("cannot access"+self.runspath)
    allruns=sorted(os.listdir(self.runspath))
    if self.runs==None:
      self.runs=allruns;
    else:
      if self.runs>=len(allruns):
        exitprog("run must be in range [0,"+str(len(allruns)-1)+"]")
      self.runs=[allruns[self.runs]]

    print "institution:",self.institution
    print "model:",self.model
    print "experiment:",self.experiment
    print "frequency:",self.frequency
    print "domain:",self.domain
    print "runs:",self.runs
    if not self.variables:
      self.variables=os.listdir(self.runspath+"/"+self.runs[0])
    print "variables:",self.variables
    print "compressed:",self.compressed


  def getRunsPath(amonpath):   # "static" class function using Callable (now really unnecessary, just still here for the example)
    amon=sorted(os.listdir(amonpath))[0]
    runspath=amonpath+"/"+amon
    return runspath
  getRunsPath=Callable(getRunsPath)

  def getVars(self):
    varspath=self.runspath+"/"+self.runs[0]
    pushd(varspath)
    shapes=[]   # for each item in shapes (a set of dims), there is a list of vars in varlist
    varlist=[]
    ntimesteps=0
    time_begin=1E6
    time_end=0
    for varname in self.variables:
      varpath=varspath+"/"+varname+"/1"
      if not os.access(varpath,os.R_OK):
        print "cannot access",varpath,"-- Skipping."
        continue
      ncfiles=os.listdir(varpath)
      vtimesteps=0
      for ncfile in ncfiles:
        f = cdms2.open(varpath+"/"+ncfile)
        #print "variables:",f.listvariable()
        #print "dimensions:",f.listdimension()
        #print "globals:",f.listglobal()

        v = f(varname)

        print varname,ncfile
        #import pdb; pdb.set_trace()    #cause break into python debugger (very handy)
        print "\tdtype:",v.dtype
        print "\tshape:",v.shape
        print "\time:",v.getTime()
        print "\tlong_name:",v.long_name

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
        varlist[varlist_id][varname]=varstr

        #print "v info:",v.info()

        # Lets get the time axis
        time = v.getTime()
        print "Found data for time:\n", time

        # And convert it into human readable format
        time = time.asComponentTime()

        mon_begin=time[0].torel('months since 1850-01-01')
        mon_end=time[-1].torel('months since 1850-01-01')
        print "time axis from",mon_begin,"to",mon_end
        mon_begin=mon_begin.value
        mon_end=mon_end.value

        if mon_begin<time_begin: 
          time_begin=mon_begin
        if mon_end>time_end:
          time_end=mon_end

        #for t in time:
        #  mon = t.torel('months since 1850-01-01')
        #  print "month:",mon,"at timestep",t

        # And look at the dimension and axis of the data
        #shape = v.shape
        #lat = v.getLatitude()
        #lon = v.getLongitude()
        #print "Spatial resolution is ", shape[1:], " covering [%f,%f] x [%f,%f]\n" % (lat[0],lat[-1],lon[0],lon[-1])

        #print len(time),"timesteps"
        #print len(v),"vs"
        vtimesteps+=len(v)

        # Now we could convert "all" the data 
        # for t,data in zip(time,v[0:10]):
        #   # Convert the time into some sane reference system
        #   day = t.torel('days since 1850-01-01')
        #   print day,":  ",data.data.__class__

      assert((time_end-time_begin+1)==vtimesteps)
      if ntimesteps<vtimesteps:
        ntimesteps=vtimesteps
      sys.stdout.flush()

    popd()
    return shapes,varlist,time_begin,time_end

  # createIdx
  def createIdxVolumes(self,shapes,varlist,time_begin,time_end):
    # Create IDX volumes based on shapes and varlist. Determines
    # resolution of volumes based on shapes and adds corresponding
    # fields in varlist to each shape.

    if len(shapes)==0 or len(shapes)!=len(varlist):
      return

    print "creating idx volumes at",self.outdir,"of",(time_end-time_begin+1),"timesteps from",time_begin,"to",time_end,"for:",shapes,varlist
    for run in self.runs:
      varspath=self.runspath+"/"+run
      for s,shape in enumerate(shapes):
        userbox     =NdBox()
        userbox.From=NdPoint(0,0,0)
        suffix=""
        if len(shape)==1:
          userbox.To  =NdPoint(shape[0]-1)
          suffix="_1d"
        elif len(shape)==2:
          userbox.To  =NdPoint(shape[1]-1,shape[0]-1)
          suffix="_2d"
        else:
          userbox.To  =NdPoint(shape[2]-1,shape[1]-1,shape[0]-1)
          suffix="_3d"
        bitsperblock=0        # Automatically determine bitmask and bitsperblock and blocksperfile and filename_template
        blocksperfile=0
        bitmask_pattern=""
        filename_template=""
        time_from=time_begin
        time_to=time_end
        time_str="time%06d/"
        fieldstr=""
        for k in varlist[s].keys():
          fieldstr+=varlist[s][k]+"+"
        outdir=self.outdir+"/"+self.institution+"/"+self.model+"/"+self.frequency+"/"+run+suffix+".idx"
        vf=IdxDataset.New(outdir,run,userbox,fieldstr[:-1],bitmask_pattern,bitsperblock,blocksperfile,filename_template,time_from,time_to,time_str)
        assert(vf)
        access=vf.createAccess()

        #write fields
        for k in varlist[s].keys():
          field=vf.getField(k)
          for ncfile in sorted(os.listdir(varspath+"/"+k+"/1")):
            print "opening",ncfile,"for writing..."
            f = cdms2.open(varspath+"/"+k+"/1/"+ncfile)
            print "getting variable",k,"for desired region ([0,360] x [-90,90])..."
            v = f(k,longitude=(0.01,360.), latitude = (-90., 90.))
            print "shape of",k,"is",v[0].shape
            ub=[userbox.To[0]+1,userbox.To[1]+1,userbox.To[2]+1]
            print "userbox:",ub
            sys.stdout.flush()
            time=v.getTime()
            # And convert it into human readable format
            time = time.asComponentTime()
            assert(len(time)==len(v))
            for t,data in zip(time,v):
              timestep=t.torel('months since 1850-01-01').value
              buf=numpy.ravel(data)
              #buf=v[t]
              #print "writing",k,"for time",timestep,"buflen=",len(buf)
              write=vf.createBoxQuery(userbox,field,timestep)
              assert(write)
              #print "buf.dtype=",buf.dtype
              #print "write.getTotSamples()",write.getTotSamples()
              #assert(write.getTotSamples()==len(buf))

              #write.setBuffer(MemoryBlock(buf))
              DTYPE=DType.New(data.dtype.name)
              write.data=PArray(ub,DTYPE,buf)

              retval=write.execute(access,ord('w'))
              #print "write returned",retval
              assert(retval==QuerySucceed)
              #assert(retval==QueryFinished)
            timestep+=len(v)
    
def exitprog(reason):
  print "exiting",reason,"..."
  popd()
  sys.exit()

    
# ############################
if __name__ == '__main__':
  cdat_basedir="/usr/sci/cedmav/data/climate/cmip5"
  outdir="/usr/sci/cedmav/data/climate/idx"

  import argparse

  parser = argparse.ArgumentParser(description="Convert CDAT data to IDX format. Expects input of the form {Institution}/{Model}/{experiment}/{frequency}/{domain}/{$$$}/{run-id}/{variable}/{???}/{filename(s).nc}")
  parser.add_argument("-n", "--nothing", action="store_true", dest="innocuous", 
                    default=False,
                    help="dry-run: does not perform any permanent action")
  parser.add_argument("-b","--basedir",default=cdat_basedir,help="base directory for climate data")
  parser.add_argument("-i","--institution")
  parser.add_argument("-m","--model")
  parser.add_argument("-e","--experiment",default="historical",help="(default: %(default)s)")
  parser.add_argument("-f","--frequency",default="mon",help="(default: %(default)s)")
  parser.add_argument("-d","--domain",default="atmos",help="(default: %(default)s)")
  parser.add_argument("-r","--run",type=int,help="(blank: all runs)")
  parser.add_argument("-v","--variables",nargs="*",help="(blank: all variables)")
  parser.add_argument("-o","--output",default=outdir,help="utput directory (default: %(default)s)")
  parser.add_argument("-c","--compressed",action="store_true",default=False)
  parser.add_argument("-t","--times",action="store_true",default=False)
  args = parser.parse_args()

  pushd(args.basedir)

  cdat=CDATConverter(args.basedir,args.institution,args.model,args.experiment,args.frequency,args.domain,args.run,args.variables,args.output,args.compressed)
  (shapes,varlist,time_begin,time_end)=cdat.getVars()
  #print "shapes:",shapes
  #print "varlist:",varlist
  print "time_begin:",time_begin
  print "time_end:",time_end

  if args.times:
    print "just printing the time data..."
    #cdat.printTimes(shapes,varlist,timesteps)
  else:
    print "converting the volume..."

    # initialize ViSUS
    app=Application();app.setCommandLine("_visuspy.pyd")
    ENABLE_VISUS_IDX()  

    #create volumes
    cdat.createIdxVolumes(shapes,varlist,time_begin,time_end)

  exitprog("normally")


