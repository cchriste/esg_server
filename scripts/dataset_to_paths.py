THREDDS_ROOT = "/esg/content/thredds/esgcet"


from xml.dom import minidom


import sys


if (len (sys.argv) < 2):

    print "Requires dataset_id argument"
    exit (1)

dataset_id = sys.argv[1]


catdoc = minidom.parse(THREDDS_ROOT + "/catalog.xml")

dataset_roots = catdoc.getElementsByTagName("datasetRoot")

cat_refs = catdoc.getElementsByTagName("catalogRef")

path = ""  # relative path to the dataset specific catalog file

for n in cat_refs:

#    print n.getAttribute("name")
    if n.getAttribute("name") == dataset_id:


        path = n.getAttribute("xlink:href")

if path == "":
    print "Error, " + dataset_id + " not found in catalog"
    exit(1)

dsdoc = minidom.parse(THREDDS_ROOT + "/" + path)

docnodes = dsdoc.getElementsByTagName("access")

for node in docnodes:

# We will use OpenDAP paths for now, assume this is a requirement
    if node.getAttribute("serviceName") == "OpenDAPServer":
        
        url = node.getAttribute("urlPath")
        
        parts = url.split("/")

        dsrootname = parts[0]
        
        abs_root = ""

        for n in dataset_roots:
            
#            print n.getAttribute("path")
            if n.getAttribute("path") == dsrootname:

                abs_root = n.getAttribute("location")

        if abs_root == "":
            print "Error:  no entry for logical dataset root " + dsrootname
            exit(1)
        
        sys.stdout.write(" ")
        sys.stdout.write(abs_root + url.lstrip(dsrootname))

        
