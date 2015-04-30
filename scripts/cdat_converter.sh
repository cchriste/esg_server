echo `date` >> /tmp/cdat_converter.log
echo $* >> /tmp/cdat_converter.log
source /usr/local/uvcdat/1.5.0/bin/setup_runtime.sh 
python ./cdat_converter.py $@ >> /tmp/cdat_converter.log
echo "====================" >> /tmp/cdat_converter.log
