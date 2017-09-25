#! /bin/bash
#
# Starts a hard convert job.
#
# Please see conf/ondemand-env.sh to customize your installation.
#
# Pass name of field as first argument. 
# Note that convert_var.py must include names of idx volumes corresponding to this field.
#

# configuration
ONDEMAND_BIN="`dirname "$0"`/.."
ONDEMAND_BIN="`cd "${ONDEMAND_BIN}"; pwd`"
ONDEMAND_CONF="`cd "${ONDEMAND_BIN}/../conf"; pwd`"
. ${ONDEMAND_CONF}/ondemand-env.sh
. ${ONDEMAND_BIN}/ondemand-defaults.sh
ONDEMAND_LOGFILE=${ONDEMAND_LOGFILE%.log}.convert_$1.log
echo "Logging to ${ONDEMAND_LOGFILE}..."

# start logging
echo "==================== starting hard convert of $1 `date` ====================" >> ${ONDEMAND_LOGFILE}

python ${ONDEMAND_BIN}/manual_conversion_scripts/convert_var.py $1 >> ${ONDEMAND_LOGFILE} 2>&1

echo "==================== finished hard convert of $1 `date` ====================" >> ${ONDEMAND_LOGFILE}


