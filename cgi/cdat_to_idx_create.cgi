#! /bin/bash

echo "Content-type:application/xml charset=utf-8"
echo "Content-Disposition: attachment; filename=\"visus.config\""
echo ""
QUERY_STRING=`echo ${QUERY_STRING} | sed -e 's/\.[^\.]*|.*/.xml/g'`
curl "http://localhost:42299/create?${QUERY_STRING}"

exit 1