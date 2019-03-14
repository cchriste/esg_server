#! /bin/bash
#
# Starts the on_demand_converter service.
#
# Please see conf/ondemand-env.sh to customize your installation.
#

DEBUG_MODE=$1

# load configuration
. "`dirname $0`"/../conf/ondemand-cfg.sh

echo "starting ondemand converter service..."
mkdir -p ${ONDEMAND_IDXPATH}
mkdir -p ${ONDEMAND_XMLPATH}

# <warning> from convert_query.py:
# nasty hack to work around bug in cdms2 when using opendap:
# solution is to run converter service from xml directory and
# to load xml files from local paths, not explicit paths
# (e.g. "filename.xml", not "/path/to/filename.xml".
#Therefore we MUST run converter server from ${ONDEMAND_XMLPATH}.
pushd ${ONDEMAND_XMLPATH}

# start logging
echo "==================== starting ondemand converter service `date` ====================" >> ${ONDEMAND_LOGFILE}

# create db
if [ ! -e ${ONDEMAND_DB} ]; then
    echo "idx.db not found, creating..."
    mkdir -p `dirname ${ONDEMAND_DB}`
    sqlite3 ${ONDEMAND_DB} < ${ONDEMAND_PATH}/code/create_tables.sql
fi

# source uv-cdat runtime
if [ -d {UVCDAT_DIR} ]; then
	source ${UVCDAT_DIR}/bin/setup_runtime.sh 
fi

# stop any running instance
${ONDEMAND_PATH}/bin/stop_service.sh

# clean up any temporary lock files
if [ -f /tmp/*.lock ]; then
	rm /tmp/*.lock
fi

# start service
if [ ${DEBUG_MODE} ]; then
  python ${ONDEMAND_PATH}/code/cdat_converter_service.py ${ARG_PORT} ${ARG_HOST} ${ARG_XMLPATH} ${ARG_IDXPATH} ${ARG_DB} ${ARG_VISUSSERVER} 2>&1
else
  python ${ONDEMAND_PATH}/code/cdat_converter_service.py ${ARG_PORT} ${ARG_HOST} ${ARG_XMLPATH} ${ARG_IDXPATH} ${ARG_DB} ${ARG_VISUSSERVER} >> $ONDEMAND_LOGFILE 2>&1 &
fi

# save pid - needed by stop_service.sh
echo $! > ${ONDEMAND_PATH}/bin/current_instance.pid

echo "==================== started ondemand converter service (pid=$!) ====================" >> ${ONDEMAND_LOGFILE}
echo "ondemand converter service started."

if [ -f /usr/local/bin/httpd-foreground.sh ]; then
echo "starting visus server."
	/usr/local/bin/httpd-foreground.sh
fi

popd
