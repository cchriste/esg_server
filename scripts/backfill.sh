
#specify the projects you want
#for project in `esglist_datasets --list-projects` ; do
for project in cmip5 ; do

    for ds in `esglist_datasets --all --select name,version --no-header $project | sed s/" | "/".v"/g` ; do

	target=/for_ganzberger1/idx/$ds.xml


	if [ ! -f $target ] ; then
	    lst=`python dataset_to_paths.py $ds`

	    time cdscan -x $target $lst > $ds.log 2>&1
	fi
	

    done


done