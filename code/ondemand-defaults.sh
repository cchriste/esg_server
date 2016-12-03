#
# Please see conf/ondemand-env.sh to customize your installation.
#

# configure defaults 
if [[ "${ONDEMAND_HOST}" = "" ]]; then
  export ONDEMAND_HOST=localhost
fi

if [[ "${ONDEMAND_PORT}" = "" ]]; then
  export ONDEMAND_PORT=42299
fi

if [[ "${ONDEMAND_LOGFILE}" = "" ]]; then
  export ONDEMAND_LOGFILE="/tmp/idx_ondemandlog"
fi

if [[ "${UVCDAT_DIR}" = "" ]]; then
  export UVCDAT_DIR="/usr/local/uvcdat/2.2.0"
fi
export UVCDAT_ANONYMOUS_LOG=yes

if [[ "${VISUSSERVER}" = "" ]]; then
  export VISUSSERVER="http://localhost/mod_visus"
fi

if [[ "${ONDEMAND_PATH}" = "" ]]; then
  export ONDEMAND_PATH="`pwd`"
fi

if [[ "${ONDEMAND_XMLPATH}" = "" ]]; then
  export ONDEMAND_XMLPATH="/data/xml"
fi

if [[ "${ONDEMAND_IDXPATH}" = "" ]]; then
  export ONDEMAND_IDXPATH="/data/idx"
fi

if [[ "${ONDEMAND_CACHE_MAX_SIZE}" = "" ]]; then
  export ONDEMAND_CACHE_MAX_SIZE=5000000000000
fi

if [[ "${ONDEMAND_DB}" = "" ]]; then
  export ONDEMAND_DB="${ONDEMAND_IDXPATH}/idx.db"
fi

# set pythonpath
export PYTHONPATH=$PYTHONPATH:$ONDEMAND_PATH:$VISUSPY_PATH

# setup command line arguments
export ARG_PORT=""
if [[ "${ONDEMAND_PORT}" != "" ]]; then
    export ARG_PORT="--port ${ONDEMAND_PORT}"
fi

export ARG_HOST=""
if [[ "${ONDEMAND_HOST}" != "" ]]; then
    export ARG_HOST="--hostname ${ONDEMAND_HOST}"
fi

export ARG_XMLPATH=""
if [[ "${ONDEMAND_XMLPATH}" != "" ]]; then
    export ARG_XMLPATH="--xmlpath ${ONDEMAND_XMLPATH}"
fi

export ARG_IDXPATH=""
if [[ "${ONDEMAND_IDXPATH}" != "" ]]; then
    export ARG_IDXPATH="--idxpath ${ONDEMAND_IDXPATH}"
fi

export ARG_DB=""
if [[ "${ONDEMAND_DB}" != "" ]]; then
    export ARG_DB="--database ${ONDEMAND_DB}"
fi

export ARG_VISUSSERVER=""
if [[ "${VISUSSERVER}" != "" ]]; then
    export ARG_VISUSSERVER="--visusserver ${VISUSSERVER}"
fi

export ARG_VISUSSERVER_USERNAME=""
if [[ "${VISUSSERVER_USERNAME}" != "" ]]; then
    export ARG_VISUSSERVER_USERNAME="--username ${VISUSSERVER_USERNAME}"
fi

export ARG_VISUSSERVER_PASSWORD=""
if [[ "${VISUSSERVER_PASSWORD}" != "" ]]; then
    export ARG_VISUSSERVER_PASSWORD="--password ${VISUSSERVER_PASSWORD}"
fi
