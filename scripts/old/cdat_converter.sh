echo `date` >> /tmp/cdat_converter.log
echo $* >> /tmp/cdat_converter.log

# mercury
source /Users/cam/code/uvcdat-build/install/bin/setup_runtime.sh
python /Users/cam/Dropbox/code/uvcdat/scripts/cdat_converter.py $@ >> /tmp/cdat_converter.log

# pcmdi11
#source /usr/local/uvcdat/1.5.0/bin/setup_runtime.sh 
#python /home/cam/code/esg_server/scripts/cdat_converter.py $@ >> /tmp/cdat_converter.log
#export PYTHONPATH=$PYTHONPATH:/home/cam/code/nvisus/build/swig

echo "====================" >> /tmp/cdat_converter.log
