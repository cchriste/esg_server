import sqlite3
import os, sys, getopt
import cdat_to_idx as conv
import convert_query
import cdat_converter_service as ccs

import OpenVisus 
from OpenVisus import *

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

def print_usage():
  print('testconvert.py -i <inputfile> -o <outputdir> [-t time] [-f fieldname]')

def main(argv):
  inputfile=''
  outputdir=''
  fieldname=''
  time=0

  try:
    opts, args = getopt.getopt(argv,"hi:o:f:t:",["ifile=","odir="])
  except getopt.GetoptError:
    print_usage()
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
       print_usage()
       sys.exit()
    elif opt in ("-i", "--ifile"):
       inputfile = arg
    elif opt in ("-o", "--odir"):
       outputdir = arg
    elif opt in ("-f"):
       fieldname = arg
    elif opt in ("-t"):
       time = int(arg)

  if((not os.path.isfile(inputfile)) or (not os.path.isdir(outputdir))):
    print('Invalid input or file or dir not found\n')
    print_usage()
    sys.exit(2)

  print('Input file is ', inputfile)
  print('Output dir is ', outputdir)

  inputdir=os.path.dirname(inputfile)

  database=outputdir+"/idx.db"

  if not os.path.isfile(database):
    print("Database file not found, creating it...")
    with open('create_tables.sql', 'r') as sql_file:
      sql_script = sql_file.read()
    db = sqlite3.connect(database)
    c = db.cursor()
    c.executescript(sql_script)
    db.commit()
    c.close()
    db.close()

  db = sqlite3.connect(database)

  ccs.init(database=database,hostname="none",port=80,xmlpath=inputdir,idxpath=outputdir,visus_server="none")

  with db:
     inputfile=os.path.abspath(inputfile)
     outputdir=os.path.abspath(outputdir)
     global idx_paths
     idx_paths,ds_id=getIdxPaths(inputfile,db)

     #if not validatePaths(idx_paths,outputdir):                                                                     
     #   print "idx files do not exist: (re)creating them"                                                           
     force=False

      # if force recreate, delete existing entries in database                                                       
     if force:
         cur=db.cursor()

         cur.execute("DELETE from datasets where ds_id=%d"%ds_id[0])
         for path in idx_paths:
                  cur.execute("DELETE from idxfiles where ds_id=%d"%ds_id[0])
                  cur.execute("DELETE from midxfiles where ds_id=%d"%ds_id[0])

     if len(idx_paths)==0 or force:
          conv.cdat_to_idx(inputfile,outputdir,db)

          print("done creating idx volumes for",inputfile)
          idx_paths,ds_id=getIdxPaths(inputfile,db)
     else:
          print("idx volumes already exist for",inputfile)

  db.close()

  dataset=Dataset_loadDataset(outputdir+"/"+idx_paths[0])
  print(dataset)
  f=dataset.getDefaultField()
  
  print("exported fields:")
  for ef in dataset.getFields():
    print(ef.name)

  if(fieldname==''):
    field=f.name
  else:
    field=fieldname
  timestep=time
  hz=-1
  box=None

  try:
    print(">>> Converting field "+field+" at time "+str(timestep))
    convert_query.convert(idx_paths[0],field,timestep,box,hz,database)
  except (Exception, e):
    print("Exception: ",e)


if __name__ == "__main__":
   main(sys.argv[1:])
