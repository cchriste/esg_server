#! /bin/bash

xml=`curl "http://localhost:42299/create?dataset=/for_ganzberger1/idx/xml/cmip5.output1.FIO.fio-esm.historical.mon.ocean.Omon.r2i1p1.v20120522.xml&destination=/for_ganzberger1/idx/idx&server=http://pcmdi11.llnl.gov:8080/mod_visus&username=root&password=visus&service=http://localhost:42299"`

echo "Content-type:text/xml"
echo $xml
