from sys import argv,exit
import cdms2


if len(argv) < 2:
    print "Usage: %s <filename.nc>" % argv[0]
    exit(0)



# This gets us a special file handle
file = cdms2.open(argv[1])

# For demonstration purposes let's extract the field name which is
# typically the last variable. In practice this can be gotten from the
# directory names for example
var_name = file.getVariables()[-1].id

# This gets us a handle to the data but not the data itself.
data_handle = file[var_name]

# Lets get the time axis
time = data_handle.getTime()
print "Found data for time:\n", time

# And convert it into human readable format
time = time.asComponentTime()


# And look at the dimension and axis of the data
shape = data_handle.shape
lat = data_handle.getLatitude()
lon = data_handle.getLongitude()
print "Spatial resolution is ", shape[1:], " covering [%f,%f] x [%f,%f]\n" % (lat[0],lat[-1],lon[0],lon[-1])


# Now we could convert "all" the data 
for t,data in zip(time,data_handle[0:10]):

    # Convert the time into some sane reference system
    month = t.torel('month since 1800-1-1')

    print month,":  ",data.data.__class__
