#! /bin/bash
#
# Starts the on_demand_converter service.
#
# Please see conf/ondemand-env.sh to customize your installation.
#

# configuration
ONDEMAND_BIN="`dirname "$0"`"
ONDEMAND_BIN="`cd "${ONDEMAND_BIN}"; pwd`"
ONDEMAND_CONF="`cd "${ONDEMAND_BIN}/../conf"; pwd`"
. ${ONDEMAND_CONF}/ondemand-env.sh
. ${ONDEMAND_BIN}/ondemand-defaults.sh

# start logging
echo "==================== starting ondemand converter service `date` ====================" >> ${ONDEMAND_LOGFILE}

# create db
if [ ! -e ${ONDEMAND_DB} ]; then
    echo "idx.db not found, creating..."
    sqlite3 ${ONDEMAND_DB} < ${ONDEMAND_BIN}/create_tables.sql
fi

# source uv-cdat runtime
source ${UVCDAT_DIR}/bin/setup_runtime.sh 

# stop any running instance
pid=${ONDEMAND_BIN}/current_instance.pid
if [ -f $pid ]; then
  TARGET_ID="$(cat "$pid")"
  if [[ $(ps -p "$TARGET_ID" -o comm=) =~ "python" ]]; then
    echo "stopping ondemand converter service..."
    kill "$TARGET_ID" && rm -f "$pid"
  fi
fi

# start service
python ${ONDEMAND_BIN}/cdat_converter_service.py ${ARG_PORT} ${ARG_HOST} ${ARG_XMLPATH} ${ARG_IDXPATH} ${ARG_DB} ${ARG_VISUSSERVER} ${ARG_VISUSSERVER_USERNAME} ${ARG_VISUSSERVER_PASSWORD} >> $ONDEMAND_LOGFILE 2>&1 &
echo $! > $pid

echo "==================== started ondemand converter service (pid=$!) ====================" >> ${ONDEMAND_LOGFILE}
echo "ondemand converter service started."

#TODO: print current settings for port and paths

