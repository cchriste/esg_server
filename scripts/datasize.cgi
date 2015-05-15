#! /bin/bash

cachesz=`du -hs /for_ganzberger1/idx/idx`
diskfree=`df -h /for_ganzberger1/idx/idx`
echo "Content-type: text/html"
echo ""
echo "<html>"
echo "<head>"
echo "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">"
echo "<title>IDX Cache Size</title>"
echo "</head>"
echo "<body>"
echo "<h3>IDX Cache Size</h3>"
echo "<li>Cache Size: <pre>${cachesz}</pre></li>"
echo "<li>Free Space: <pre>${diskfree}</pre></li>"
echo "</body></html>"

exit 1
