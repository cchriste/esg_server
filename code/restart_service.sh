#! /bin/bash
#
# Restarts the on_demand_converter service.
#

# configuration
ONDEMAND_BIN="`dirname "$0"`"
ONDEMAND_BIN="`cd "${ONDEMAND_BIN}"; pwd`"
${ONDEMAND_BIN}/stop_service.sh
${ONDEMAND_BIN}/start_service.sh $*
