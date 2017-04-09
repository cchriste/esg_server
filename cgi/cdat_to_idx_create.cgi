#! /bin/bash

echo "Content-type:application/xml charset=utf-8"
echo "Content-Disposition: attachment; filename=\"visus.config\""
echo ""
QUERY_STRING=`echo ${QUERY_STRING} | sed -e 's/\.[^\.]*|.*/.xml/g'`
QUERY_STRING=`echo ${QUERY_STRING} | sed -e 's/\.v[0-9]\+\.xml/.xml/g'`
#echo ${QUERY_STRING}    #use for debugging
curl "http://localhost:42299/create?${QUERY_STRING}"

exit 1