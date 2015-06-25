#! /bin/python

#
# Sort datasets produced by `find . -name "*.nc"  ../ondemand/xml/all_nc_files.txt` 
# into a group of text files listing all members of a dataset per file.
#

import sys
import os
import re
from subprocess import call

if len(sys.argv) < 2:
    print "Usage: python collect_datasets.py <list_of_full_paths_to_all_nc_files>"
    sys.exit(-1)

filelist=open(sys.argv[1],'r')

datasets={}
for value in filelist:
    key = re.sub("/","_",re.match(".*/r[0-9]+i[0-9]+p[0-9]+", value).group(0))[2:]
    if not datasets.has_key(key):
        datasets[key]=[]
    datasets[key].append(value[:-1])

outdir="../ondemand/xml/"
for key in datasets.keys():
    call(["cdscan","-x",outdir+key+".xml",str(datasets[key])])
