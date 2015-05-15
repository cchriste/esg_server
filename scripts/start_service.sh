#! /bin/bash

LOGFILE=/tmp/cdat_to_idx_service.log
echo `date` >> $LOGFILE
echo $* >> $LOGFILE

#mercury
#SCRIPTS=/Users/cam/Dropbox/code/uvcdat/scripts

#pcmdi11
SCRIPTS=/home/cam/code/esg_server/scripts

#mercury
#DB=/Users/cam/Dropbox/code/uvcdat/data/idx/idx.db

#pcmdi11
DB=/for_ganzberger1/idx/idx/idx.db 


if [ -e $DB ]; then
    sqlite3 $DB < $SCRIPTS/create_tables.sql
fi

# mercury
#source /Users/cam/code/uvcdat-build/install/bin/setup_runtime.sh
#python /Users/cam/Dropbox/code/uvcdat/scripts/cdat_converter_service.py --database $DB >> $LOGFILE 2>&1 &

# pcmdi11
source /usr/local/uvcdat/1.5.0/bin/setup_runtime.sh 
export PYTHONPATH=$PYTHONPATH:/home/cam/code/nvisus/build/swig
python $SCRIPTS/cdat_converter_service.py --port 42299 --hostname localhost --database $DB >> $LOGFILE 2>&1 &

echo "====================" >> $LOGFILE
