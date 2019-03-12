#! /bin/bash
#
# Starts a manual conversion job.
#
# Please see conf/ondemand-env.sh to customize your installation.
#
# Pass name of field as first argument. 
# Note that convert_var.py must include names of idx volumes corresponding to this field.
#

# load configuration
. "`dirname $0`"/../../conf/ondemand-cfg.sh

ONDEMAND_LOGFILE=${ONDEMAND_LOGFILE%.log}.convert_$1.log
echo "Logging to ${ONDEMAND_LOGFILE}..."

# start logging
echo "==================== starting manual conversion of $1 `date` ====================" >> ${ONDEMAND_LOGFILE}

python ${ONDEMAND_PATH}/bin/manual_conversion_scripts/convert_var.py $1 >> ${ONDEMAND_LOGFILE} 2>&1

echo "==================== finished manual conversion of $1 `date` ====================" >> ${ONDEMAND_LOGFILE}


