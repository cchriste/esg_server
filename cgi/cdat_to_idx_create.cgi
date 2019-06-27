#!/bin/bash

#echo "Content-type:application/xml charset=utf-8"
#echo "Content-Disposition: attachment; filename=\"visus.config\""
#echo "Access-Control-Allow-Origin: *"  #do we need this??
#echo ""
#echo ${QUERY_STRING}    #use for debugging

#query string changed after link was recreated on 2017/09
#QUERY_STRING=`echo ${QUERY_STRING} | sed -e 's/cmip5rt/cmip5/g' | sed -e 's/\.[^\.]*\.[^\.]*|.*/.xml/g'`

# configuration
. ../conf/ondemand-cfg.sh

QUERY_STRING=`echo ${QUERY_STRING}` #| sed -e 's/cmip5rt/cmip5/g' | sed -r -e 's/\.v[0-9]+(%7C|\|)+.*/.xml/g'`
echo "query: " ${QUERY_STRING} > /tmp/query_string.out  #use for debugging

ts=`date +%s`

curl "http://${ONDEMAND_HOST}:${ONDEMAND_PORT}/create?${QUERY_STRING}&ts=$ts" -o ${ONDEMAND_LOGFILE}

# wait for result in file
#while [ ! -f /tmp/${ts}.out ]
#do
#    sleep 2
#    n=`date +%s`
#    if [ $(($n-$ts)) -gt 10 ]; then
#	break
#    fi
#done

#python ${ONDEMAND_PATH}/code/get_last_dataset.py /tmp/${ts}.out > /tmp/last_attempt.out
last_idx=`python ${ONDEMAND_PATH}/code/get_last_dataset.py /tmp/${ts}.out`
echo $last_idx > /tmp/last_idx.out

server="${VISUSSERVER}?"
#dataset_id=`echo ${QUERY_STRING} | awk -F'[=&]' '{print $2}'` 

#dataset=`echo ${QUERY_STRING} | cut -d'=' -f 2 | sed -r -e 's/\.(nc|xml)+//'`
#append="_idx"
#"-lon_lat_plev_time_idx"
#dataset="$dataset$append"

#echo $dataset_id > /tmp/dataset_name.out
#python map_files.py $dataset_id > /tmp/dataset_path.out
#$first="`head -n1 /tmp/dataset_path.out`"
#echo $first > /tmp/first_dataset.out
#echo "http://${ONDEMAND_HOST}:${ONDEMAND_PORT}/create?{dataset=}" > /tmp/ondemand_config.out

palette="rich"
vr=0  # this should depend on the dataset dims


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
#FIXME: it's not working yet for general datasets, so leave dataset out for now and just show something pretty
#echo "<script>window.open(\"${VISUSSERVER}/viewer/viewer.html?server=$( rawurlencode $server )&palette=$palette&palette_min=0.0&palette_max=0.0&dataset=nature_2007_aer1_hourly\",'_self');</script>"
#echo "<script>window.open(\"${VISUSSERVER}/viewer/viewer.html?server=$( rawurlencode $server )&dataset=$( rawurlencode $dataset )&palette=$palette&vr=$vr&palette_min=0.0&palette_max=0.0&dataset=nature_2007_aer1_hourly\",'_self');</script>"
echo "<script>window.open(\"https://aims2.llnl.gov/visus/viewer/viewer.html?server=$( rawurlencode $server )&dataset=$last_idx\",'_self');</script>"

echo "</head></html>"
