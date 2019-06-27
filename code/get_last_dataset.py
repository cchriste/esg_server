import subprocess
import xml.etree.ElementTree as ET
import sys
import datetime
import time
import os

#result = subprocess.run(['curl', '-v', 'http://localhost/mod_visus?action=list'], stdout=subprocess.PIPE)

file_path=sys.argv[1]

start_time = datetime.datetime.now()

while not (os.path.exists(file_path) || os.stat(file_path).st_size) < 16):
    time.sleep(1)
    el_time = datetime.datetime.now()-start_time
    if (el_time.seconds > 10):
        print("ERROR", file_path+" not found")
        exit(1)

        
f = open(file_path,"r+")

xml = ET.fromstring(f.read()) #result.stdout)
#print(result.stdout)
#for table in xml.findall('.//dataset'):
#  for child in table:
#     print(child.tag, child.attrib['name'])

idx_list=[]
for elem in xml.iter():
    if(elem.tag=="dataset"):
      #if(elem.attrib['name'].endswith("_idx")):
          idx_list.append(elem.attrib['name'])
          #print(elem.tag, elem.attrib['name'])

print(idx_list[-1]+"_idx")

outf=open("/tmp/last_attempt.out","w")
outf.write(idx_list[-1]+"_idx")
outf.close()

