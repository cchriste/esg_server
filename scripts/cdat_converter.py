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
# or...
#
# Less sophisticated version, no threads, just file-based locking.
# "Advantage" is that caller is blocked until conversion is complete.
# But since caller is probably also threaded, this may be sufficient.
#
#****************************************************



def convert(dataset,field,time,box,hz,idxdir,database):
    """Converts a timestep of a field of a cdat dataset to idx, using the database to find the matching idx volume for the given dataset field."""

    # lookup idx corresponding to dataset field
    db=web.db.open(database)
    xml=db.select("xml in idx")
    #...yeah

    

    # open xml
    import cdms2
    f=cdms2.open(xml)
    v=f(field)
 
    # initialize ViSUS
    import visuspy as Visus
    app=Visus.Application(); app.setCommandLine("_visuspy.pyd")
    Visus.ENABLE_VISUS_IDX()  

    buf=numpy.ravel(v)
    write=vf.createBoxQuery(userbox,field,timestep)
    assert(write)
    DTYPE=DType.New(data.dtype.name)
    write.data=PArray(ub,DTYPE,buf)
    retval=write.execute(access,ord('w'))
    assert(retval==QuerySucceed)
    



# ############################
if __name__ == '__main__':
    database="/Users/cam/Dropbox/code/uvcdat/data/idx/idx.db"

    import argparse
    parser = argparse.ArgumentParser(description="Convert CDAT data to IDX format.")
    parser.add_argument("-n", "--nothing", action="store_true", dest="innocuous", 
                        default=False,
                        help="dry-run: does not perform any permanent action")
    parser.add_argument("-i","--idx",required=True,help="path to idx volume")
    parser.add_argument("-f","--field",required=True,help="field to read (e.g. ta)")
    parser.add_argument("-t","--time",required=True,help="timestep")
    parser.add_argument("-b","--box",default="",help="region to convert, default all")
    parser.add_argument("-z","--hz",default=-1,help="hz level, default max")
    parser.add_argument("--database",default=idxdb,help="alternate database")
    args = parser.parse_args()

    return convert(args.dataset,args.field,args.time,args.box,args.hz,args.idxdir,args.database)
