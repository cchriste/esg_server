#! /bin/bash

echo "Content-type:application/xml charset=utf-8"
echo "Content-Disposition: attachment; filename=\"visus.config\""
echo "Access-Control-Allow-Origin: *"  #do we need this??
echo ""
#echo ${QUERY_STRING}    #use for debugging
QUERY_STRING=`echo ${QUERY_STRING} | sed -e 's/cmip5rt/cmip5/g' | sed -e 's/\.[^\.]*\.[^\.]*|.*/.xml/g'`
#echo ${QUERY_STRING}    #use for debugging
curl "http://localhost:42299/create?${QUERY_STRING}"

exit 1
