#
# Please see conf/ondemand-env.sh to customize your installation.
#

# configure defaults 
if [[ "${ONDEMAND_HOST}" = "" ]]; then
  ONDEMAND_HOST=localhost
fi

if [[ "${ONDEMAND_PORT}" = "" ]]; then
  ONDEMAND_PORT=42299
fi

if [[ "${ONDEMAND_LOGFILE}" = "" ]]; then
  ONDEMAND_LOGFILE="/tmp/idx_ondemandlog"
fi

if [[ "${UVCDAT_DIR}" = "" ]]; then
  UVCDAT_DIR="/usr/local/uvcdat/2.2.0"
fi

if [[ "${VISUSSERVER}" = "" ]]; then
  VISUSSERVER="http://localhost/mod_visus"
fi

if [[ "${ONDEMAND_XMLPATH}" = "" ]]; then
  ONDEMAND_XMLPATH="/data/xml"
fi

if [[ "${ONDEMAND_IDXPATH}" = "" ]]; then
  ONDEMAND_IDXPATH="/data/idx"
fi

# set pythonpath
PYTHONPATH=$PYTHONPATH:$VISUSPY_PATH

# setup command line arguments
ARG_PORT=""
if [[ "${ONDEMAND_PORT}" != "" ]]; then
    PORT="--port ${ONDEMAND_PORT}"
fi

ARG_HOST=""
if [[ "${ONDEMAND_HOST}" != "" ]]; then
    ARG_HOST="--hostname ${ONDEMAND_HOST}"
fi

ARG_XMLPATH=""
if [[ "${ONDEMAND_XMLPATH}" != "" ]]; then
    ARG_XMLPATH="--xmlpath ${ONDEMAND_XMLPATH}"
fi

ARG_IDXPATH=""
if [[ "${ONDEMAND_IDXPATH}" != "" ]]; then
    ARG_IDXPATH="--idxpath ${ONDEMAND_IDXPATH}"
fi

ARG_DB=""
if [[ "${ONDEMAND_DB}" != "" ]]; then
    ARG_DB="--database ${ONDEMAND_DB}"
fi

ARG_VISUSSERVER=""
if [[ "${VISUSSERVER}" != "" ]]; then
    ARG_VISUSSERVER="--visusserver ${VISUSSERVER}"
fi

ARG_VISUSSERVER_USERNAME=""
if [[ "${VISUSSERVER_USERNAME}" != "" ]]; then
    ARG_VISUSSERVER_USERNAME="--username ${VISUSSERVER_USERNAME}"
fi

ARG_VISUSSERVER_PASSWORD=""
if [[ "${VISUSSERVER_PASSWORD}" != "" ]]; then
    ARG_VISUSSERVER_PASSWORD="--password ${VISUSSERVER_PASSWORD}"
fi
