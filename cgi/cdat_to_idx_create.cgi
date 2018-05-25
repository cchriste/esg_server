#!/bin/bash

#echo "Content-type:application/xml charset=utf-8"
#echo "Content-Disposition: attachment; filename=\"visus.config\""
#echo "Access-Control-Allow-Origin: *"  #do we need this??
#echo ""
####echo ${QUERY_STRING}    #use for debugging

#query string changed after link was recreated on 2017/09
#QUERY_STRING=`echo ${QUERY_STRING} | sed -e 's/cmip5rt/cmip5/g' | sed -e 's/\.[^\.]*\.[^\.]*|.*/.xml/g'`

QUERY_STRING=`echo ${QUERY_STRING} | sed -e 's/cmip5rt/cmip5/g' | sed -r -e 's/\.v[0-9]+(%7C|\|)+.*/.xml/g'`
#echo ${QUERY_STRING} > /tmp/query_string.out  #use for debugging
curl "http://localhost:42299/create?${QUERY_STRING}" -o /tmp/idx_create.out

server="http://localhost:80/mod_visus?"

dataset=`echo ${QUERY_STRING} | cut -d'=' -f 2 | sed -r -e 's/\.(nc|xml)+//'`
append="-lon_lat_plev_time_idx"
dataset="$dataset$append"
#echo $dataset > /tmp/dataset_name.out

palette=""
vr=1
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
        * )               printf -v o '%%%02X' "'$c"
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
echo "<script>window.open(\"http://localhost/viewer?server=$( rawurlencode $server )&dataset=$( rawurlencode $dataset )&palette=$palette&vr=$vr\",'_self');</script>"
echo "</head></html>"
