###############################################################################
# base path used by all other scripts - should ONLY be set here
ONDEMAND_PATH="`cd \`dirname "$0"\`/..; pwd`"


###############################################################################
# configuration options - modify to suit the needs of your installation.

#   ONDEMAND_HOST           - host to listen for ondemand requests
ONDEMAND_HOST=localhost

#   ONDEMAND_PORT           - port to listen for ondemand requests
ONDEMAND_PORT=42299

#   ONDEMAND_LOGFILE        - path to logfile
ONDEMAND_LOGFILE="/tmp/idx_ondemand.log"

#   UVCDAT_DIR              - path to uvcdat installation
UVCDAT_DIR="/usr/local/uvcdat/2.2.0"

#   VISUSPY_PATH            - path to visuspy install dir (if not installed in system-accessible location)
VISUSPY_PATH="${ONDEMAND_PATH}/code"

#   VISUSSERVER             - server that hosts idx volumes (must be able to access them)
VISUSSERVER="http://localhost"

#   ONDEMAND_XMLPATH        - path to cdat xml files created by uvcdat cdscan utility
ONDEMAND_XMLPATH="/data/xml"

#   ONDEMAND_IDXPATH        - destination path for idx volumes
ONDEMAND_IDXPATH="/data/idx"

#   ONDEMAND_CACHE_MAX_SIZE - maximum size of ondemand cache (located in ONDEMAND_IDXPATH) in bytes
ONDEMAND_CACHE_MAX_SIZE=5000000000000

#   ONDEMAND_DB             - path to idx-to-cdat (xml) database
ONDEMAND_DB="${ONDEMAND_IDXPATH}/idx.db"


###############################################################################
# system-wide exports

export UVCDAT_ANONYMOUS_LOG=yes
export PYTHONPATH=$PYTHONPATH:$ONDEMAND_PATH:$VISUSPY_PATH


###############################################################################
# command line arguments for cdat_converter_service.py

ARG_PORT=""
if [[ "${ONDEMAND_PORT}" != "" ]]; then
    ARG_PORT="--port ${ONDEMAND_PORT}"
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

    # generate ondemand-server.js used by ondemand.php
    echo -e "// AUTOGENERATED BY ondemand-cfg.sh\n// visus server that user is forwarded to after conversion.\nVISUSSERVER='${VISUSSERVER}'" > ondemand-server.js
fi
