#
# Ondemand configuration options
#
# Modify any parameters to suit the needs of your installation.
# Modifications are shell env vars of the form VAR=value.
#
#   ONDEMAND_PATH           - full path to ../code (added to PYTHONPATH in order to import .py files)
#   ONDEMAND_HOST           - host to listen for ondemand requests (default is localhost)
#   ONDEMAND_PORT           - port to listen for ondemand requests (default is 42299)
#   ONDEMAND_LOGFILE        - path to logfilee (default /tmp/idx_ondemand.log)
#   UVCDAT_DIR              - path to uvcdat installation (default is /usr/local/uvcdat/2.2.0)
#   VISUSPY_PATH            - path to visuspy install dir (if not installed in system-accessible location)
#   VISUSSERVER             - server with which to register idx volumes (default is http://localhost)
#                           - (server address is also shared with clients, so it should be externally accessible)
#   ONDEMAND_XMLPATH        - path to cdat xml files created by uvcdat cdscan utility (default is /data/xml)
#   ONDEMAND_IDXPATH        - destination path for idx volumes (default is /data/idx)
#   ONDEMAND_CACHE_MAX_SIZE - maximum size of ondemand cache in bytes (ONDEMAND_IDXPATH, default is 5000000000000, 5T)
#   ONDEMAND_DB             - path to idx-to-cdat (xml) database (default is IDXPATH/idx.db)
#

ONDEMAND_PATH="`dirname "$0"`"
ONDEMAND_PATH="`cd "${ONDEMAND_PATH}"; pwd`"
echo "ONDEMAND_PATH: " $ONDEMAND_PATH

ONDEMAND_PORT="/foo/bar"

. ${ONDEMAND_PATH}/conf/ondemand-defaults.sh

echo "ONDEMAND_PORT: " $ONDEMAND_PORT
echo "ARG_PORT: " $ARG_PORT
