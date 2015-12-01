#! /bin/bash
#
# Stops the on_demand_converter service.
#

# configuration
ONDEMAND_BIN="`dirname "$0"`"
ONDEMAND_BIN="`cd "${ONDEMAND_BIN}"; pwd`"

# stop any running instance
pid=${ONDEMAND_BIN}/current_instance.pid
if [ -f $pid ]; then
  TARGET_ID="$(cat "$pid")"
  shopt -s nocasematch
  if [[ $(ps -p "$TARGET_ID" -o comm=) =~ "python" ]]; then
    echo "stopping ondemand converter service..."
    kill "$TARGET_ID" && rm -f "$pid"
    echo "ondemand converter service stopped."
  fi
fi



