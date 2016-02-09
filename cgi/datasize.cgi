#! /bin/bash

cachesz=`du --max-depth=0  --exclude "*.idx*" /for_ganzberger1/idx/ondemand/idx/acme-test*`
cacheszh=`du -h --max-depth=1  /for_ganzberger1/idx/ondemand/idx`
diskfree=`df -h /for_ganzberger1/idx/ondemand/idx`
echo "Content-type: text/html"
echo ""
echo "<html>"
echo "<head>"
echo "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">"
echo "<title>IDX Cache Size</title>"
echo "</head>"
echo "<body>"
echo "<script language=\"JavaScript\" type=\"text/javascript\">"
echo "<!--"
echo "function ClearCache(){"
echo "  xmlhttp=new XMLHttpRequest();"
echo "  xmlhttp.open(\"GET\",\"/cgi-bin/clear_sample_datasets.cgi\",false);"
echo "  xmlhttp.send();"
#echo "  xmlDoc=xmlhttp.responseText;"
#echo "  alert(xmlDoc);"
echo "  location.reload();"
echo "}"
echo "//-->"
echo "</script>"
echo "<h3>IDX Cache Size</h3>"
echo "<h4>ACME-TEST sample datasets</h4>"
echo "<pre>${cachesz}</pre>"
echo "<button type=\"button\" onclick=\"ClearCache()\">Clear Sample Datasets Cache</button>"
echo "<h4>All datasets</h4>"
echo "<li>Cache Size:</li>"
echo "<pre>${cacheszh}</pre>"
echo "<li>Free Space: <pre>${diskfree}</pre></li>"
echo "</body></html>"

exit 1