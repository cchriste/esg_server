import sqlite3
import os
import cdat_to_idx as conv

def getIdxPaths(cdat_dataset,db):
    """Looks in sqlite database db for idxfiles entries that refer to cdat_database. Returns a list of such entrie\
s."""
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
    
database='/data/idx/idx.db'
db = sqlite3.connect(database)

inputfile="/data/xml/ta_Amon_CESM1-WACCM_historical_r1i1p1_185001-200512.nc"
outputdir="/data/idx"

with db:
   inputfile=os.path.abspath(inputfile)
   outputdir=os.path.abspath(outputdir)
   idx_paths,ds_id=getIdxPaths(inputfile,db)

   #if not validatePaths(idx_paths,outputdir):                                                                     
   #   print "idx files do not exist: (re)creating them"                                                           
   force=True

    # if force recreate, delete existing entries in database                                                       
   if force:
       cur=db.cursor()
       cur.execute("DELETE from datasets where ds_id=%d"%ds_id[0])
       for path in idx_paths:
                cur.execute("DELETE from idxfiles where ds_id=%d"%ds_id[0])
                cur.execute("DELETE from midxfiles where ds_id=%d"%ds_id[0])

   if len(idx_paths)==0 or force:
        conv.cdat_to_idx(inputfile,outputdir,db)

        print "done creating idx volumes for",inputfile
        idx_paths,ds_id=getIdxPaths(inputfile,db)
   else:
        print "idx volumes already exist for",inputfile

db.close()