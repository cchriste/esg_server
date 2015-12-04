#! /bin/bash

echo "Content-type:application/xml charset=utf-8"
echo "Content-Disposition: attachment; filename=\"visus.config\""
echo ""
curl "http://localhost:42299/create?${QUERY_STRING}"

exit 1