#! /bin/bash

echo "Content-type: text/html"
echo ""
echo "<html>"
echo "<head>"
echo "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">"
echo "<title>Sample datasets cleared!</title>"
echo "</head>"
echo "<body>"
curl "http://localhost:42299/clear"
echo "<p>Sample datasets cleared!"
echo "</body></html>"


exit 1
