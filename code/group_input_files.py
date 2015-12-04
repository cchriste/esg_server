#!/usr/bin/env python

#
# Create lists of input files grouped by experiment key.
#
# You can use the results like this:
# for f in `ls *.list`; do cdscan -x /scratch/for_ganzberger1/idx/ondemand/xml/${f%.list}.xml $f; done


import os
import re

basepath="/scratch/for_ganzberger1/idx/ondemand/tmp"
datasets={}

# Set the directory you want to start from
rootDir = '/cmip5_gdo2/data/cmip5/output1'
for dirName, subdirList, fileList in os.walk(rootDir):
    #print('Found directory: %s' % dirName)
    m=re.search("(.*/r\d\d?i\d\d?p\d\d?).*",dirName)
    if not m:
        continue
    dirKey=m.group(1);
    #print(' ...base directory: %s' % dirKey
    if not datasets.has_key(dirKey):
        datasets[dirKey]=[]
    for fname in fileList:
        fullpathFname=dirName+'/'+fname
        #print('\t'+fullpathFname)
        datasets[dirKey].append(fullpathFname)

for key in datasets:
    outname=basepath+'/'+re.sub('/','_',key[1:])+".list"
    print("writing "+outname)
    f=open(outname,'w')
    for i in datasets[key]:
        f.write(i+'\n')



