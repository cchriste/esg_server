#! /bin/bash
#
# Restarts the on_demand_converter service.
#

# load configuration
. "`dirname $0`"/../conf/ondemand-cfg.sh
${ONDEMAND_PATH}/bin/stop_service.sh
${ONDEMAND_PATH}/bin/start_service.sh $*
