from sys import argv,exit
import cdms2 # This is the data access library of cdat
import numpy as np

#
# This code demonstrates how to access netcdf files through cdat's cdms2 library
# with the goal of converting it into ViSUS IDX format
#

# First lets try to open a data set. Note that this can be either a *.nc file
# which is an actual netcdfs file or it can be an xml file which references
# multiple nc files to simulate a bigger data set. E.g. when there there too
# many time steps nc files are typically separated into time chuncks that can be
# glued using an xml file. See
#
# http://www2-pcmdi.llnl.gov/cdat/tips_and_tricks/file_IO/virtual_concat.html
#
input = cdms2.open(argv[1])


# This is now an abstract CDMS file 
print input


# Now lets see what variables we actually have in the file. This should get us a
# ton of meta data some of which we will have to preserve, especially the global
# bounds. 
fields=input.getVariables()
for f in fields:
    print f.id

if len(argv) < 3:
    print "Let's pick one of these variable names from the list and do\n%s %s <var-name>\n" % (argv[0],argv[1])
    exit(1)


# Now we pick one variable by suplying a string as second argument
handle = input[argv[2]]

# THe reason I called this a handle is that it actually is just a reference to
# potential data at this point this handle looks like an array but we have not
# actually read any data. 
print handle

# Also we can get even more information by looking at the actual axes
handle.getDomain()


# However, we clearly see the shape which tells us the dimensions. The order is
# [time,z,y,x] or for 2D data [time,y,x]
print handle.shape

# This call finally actually get the data for the first time step
data = handle[0]

# So we now only have the spatial dimension left
print data.shape

# At this point data is a "masked_array" which mean an array which might have
# some data missing. Missing data is indicated by a special fill value So
# whenever data[z,y,x] = data.fill_value the data should be considered
# invalid. However, at its core this is simply a numpy array. In particular,
# there is a numpy arrary inside
print data.data.__class__    


# Now we can for example iterate through all time steps
for t in xrange(0,handle.shape[0]):

    # Get the data for this time step
    data = handle[t].data

    # and, for example, write it to a tmp file. Note that numpy guarantees that
    # this file is always in C-order -- row major --
    data.tofile("tmp.raw")

    # Since a numpy array is simply a flat array we can now feed that file to
    # the visus conversion
    
    # convert_to_visus() 
    
