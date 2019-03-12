#! /bin/bash
#
# Stops the on_demand_converter service.
#

# load configuration
. "`dirname $0`"/../conf/ondemand-cfg.sh

# stop any running instance
pid=${ONDEMAND_PATH}/bin/current_instance.pid
if [ -f $pid ]; then
  TARGET_ID="$(cat "$pid")"
  shopt -s nocasematch
  if [[ $(ps -p "$TARGET_ID" -o comm=) =~ "python" ]]; then
    echo "stopping ondemand converter service..."
    kill "$TARGET_ID" && rm -f "$pid"
    echo "ondemand converter service stopped."
  fi
fi



