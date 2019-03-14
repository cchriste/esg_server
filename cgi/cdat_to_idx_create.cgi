#!/bin/bash

#echo "Content-type:application/xml charset=utf-8"
#echo "Content-Disposition: attachment; filename=\"visus.config\""
#echo "Access-Control-Allow-Origin: *"  #do we need this??
#echo ""
####echo ${QUERY_STRING}    #use for debugging

#query string changed after link was recreated on 2017/09
#QUERY_STRING=`echo ${QUERY_STRING} | sed -e 's/cmip5rt/cmip5/g' | sed -e 's/\.[^\.]*\.[^\.]*|.*/.xml/g'`

# configuration
. ondemand-cfg.sh

QUERY_STRING=`echo ${QUERY_STRING} | sed -e 's/cmip5rt/cmip5/g' | sed -r -e 's/\.v[0-9]+(%7C|\|)+.*/.xml/g'`
#echo "query: " ${QUERY_STRING} > /tmp/query_string.out  #use for debugging
curl "http://${ONDEMAND_HOST}:${ONDEMAND_PORT}/create?${QUERY_STRING}" -o ${ONDEMAND_LOGFILE}

server="${VISUSSERVER}/mod_visus?"

dataset=`echo ${QUERY_STRING} | cut -d'=' -f 2 | sed -r -e 's/\.(nc|xml)+//'`
append="_idx"
#"-lon_lat_plev_time_idx"
dataset="$dataset$append"
#echo $dataset > /tmp/dataset_name.out

palette="rich"
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
echo "<script>window.open(\"${VISUSSERVER}/viewer?server=$( rawurlencode $server )?&dataset=$( rawurlencode $dataset )&palette=$palette&vr=$vr\",'_self');</script>"
echo "</head></html>"
