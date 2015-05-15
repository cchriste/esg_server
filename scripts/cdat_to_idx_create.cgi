#! /bin/bash

xml=`curl "http://localhost:42299/create?${QUERY_STRING}"`
echo "Content-type:text/xml"
echo "Content-Disposition: attachment; filename=\"visus.config\""
echo ""
echo $xml

exit 1
