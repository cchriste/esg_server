#! /bin/bash
#
# Cleanup idx cache by removing least recently accessed files down to at least neutral watermark level.
#
# Please see conf/ondemand-env.sh to customize your installation.
#

# load configuration
. "`dirname $0`"/../conf/ondemand-cfg.sh

# start logging
echo "==================================================================" >> ${ONDEMAND_LOGFILE}
echo "==================== IDX CACHE CLEANUP `date` ====================" >> ${ONDEMAND_LOGFILE}
echo "== maximum size: ${ONDEMAND_CACHE_MAX_SIZE}" >> ${ONDEMAND_LOGFILE}

ONDEMAND_CACHE_TARGET_SIZE=`echo ${ONDEMAND_CACHE_MAX_SIZE}*0.8 | bc`
ONDEMAND_CACHE_TARGET_SIZE=${ONDEMAND_CACHE_TARGET_SIZE%.*}
echo "== target size:  ${ONDEMAND_CACHE_TARGET_SIZE}" >> ${ONDEMAND_LOGFILE}

current_size=`du -b --max-depth=0 ${ONDEMAND_IDXPATH} | cut -f 1`
echo "== current size: ${current_size}" >> ${ONDEMAND_LOGFILE}

cleanup_size=$((${current_size}-${ONDEMAND_CACHE_TARGET_SIZE}))

echo "== beginning cleanup..." >> ${ONDEMAND_LOGFILE}
echo "== need to cleanup ${cleanup_size} bytes." >> ${ONDEMAND_LOGFILE}
TMP_FILELIST=/tmp/files_by_atime.txt
find . -type f -name "*.bin" -printf '%T@ %s %p\n' | sort > ${TMP_FILELIST}

deleted_size=0
deleted_count=0
while read line
do
  if [[ ${deleted_size} -gt ${cleanup_size} ]]; then
    break;
  fi
  filesize=`echo ${line} | cut -d' ' -f 2`
  filename=`echo ${line} | cut -d' ' -f 3`
  rm ${filename}
  #echo "${filename} deleted"
  deleted_size=$((${deleted_size}+${filesize}))
  deleted_count=$((${deleted_count}+1))
done < ${TMP_FILELIST}

echo "== finished cache cleanup" >> ${ONDEMAND_LOGFILE}
echo "== removed ${deleted_count} files (${deleted_size} bytes)" >> ${ONDEMAND_LOGFILE}
echo "==================================================================" >> ${ONDEMAND_LOGFILE}
