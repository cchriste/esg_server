#!/bin/bash

#echo "Content-type:application/xml charset=utf-8"
#echo "Content-Disposition: attachment; filename=\"visus.config\""
#echo "Access-Control-Allow-Origin: *"  #do we need this??
#echo ""
####echo ${QUERY_STRING}    #use for debugging

#query string changed after link was recreated on 2017/09
#QUERY_STRING=`echo ${QUERY_STRING} | sed -e 's/cmip5rt/cmip5/g' | sed -e 's/\.[^\.]*\.[^\.]*|.*/.xml/g'`

QUERY_STRING=`echo ${QUERY_STRING} | sed -e 's/cmip5rt/cmip5/g' | sed -e 's/\.[^\.]*|.*/.xml/g'`
####echo ${QUERY_STRING}    #use for debugging
curl "http://localhost:42299/create?${QUERY_STRING}" -o /tmp/idx_create.out

# TODO: need to find a way to get the server name associated with the converter above
server="https://feedback.llnl.gov/mod_visus?"

# TODO: grep for the last (first?) dataset in the config
#dataset="cmip5.output1.CMCC.CMCC-CM.decadal1980.mon.land.Lmon.r1i1p1-lon_lat_time"
dataset="nature_2007_aer1_hourly"

palette="ExtendedCoolWarm"

#exit 1

rawurlencode() {
  local string="${1}"
  local strlen=${#string}
  local encoded=""
  local pos c o

  for (( pos=0 ; pos<strlen ; pos++ )); do
     c=${string:$pos:1}
     case "$c" in
        [-_.~a-zA-Z0-9] ) o="${c}" ;;
        * )               printf -v o '%%%02x' "'$c"
     esac
     encoded+="${o}"
  done
  echo "${encoded}"    # You can either set a return variable (FASTER)
  REPLY="${encoded}"   #+or echo the result (EASIER)... or both... :p
}

# redirect to the web viewer like this:
echo "Content-type: text/html"
echo ""
echo "<html><head>"
echo "<script>window.open(\"https://feedback.llnl.gov/webviewer/viewer.html?server=$( rawurlencode $server )&dataset=$( rawurlencode $dataset )&palette=$palette\",'_self');</script>"
echo "</head></html>"
