#
# ViSUS OnDemand Dockerfile
#

# Installation based on visus/anaconda, which has OpenVisus w/ python, webviewer, and apache mod_visus
# NOTE: - includes Docker ENVs for VISUS_HOME and CONDA_PREFIX
#       - both conda update and apt-get update have been run in the parent image
#       - for official releases, set a specific tag (e.g., visus/anaconda:1.3.8)
FROM visus/anaconda:1.3.8-newest_webviewer



#(try these by hand to see if it's all really needed: numpy, libgomp1, a2enmod cgid, cdms2, genutil, lxml, libxml2-dev...)
RUN apt-get install -y libgomp1
  #these may also be necessary:
  # cmake swig bzip2 ca-certificates curl build-essential
RUN conda install -y numpy

# enable CGI
RUN a2enmod cgid

# install conda packages
RUN conda install -c conda-forge cdms2=3.1.2=py37h6091dcd_7 && \
  conda install -c conda-forge genutil && \
  conda install -c conda-forge lxml

# # install libxml2
# RUN apt-get install -y libxml2-dev python-dev libapache2-mod-php




# Install ondemand
#[] Not sure about all the copying. At the least, let's use an install script.
#[] install script should set cfg params in respective files

# add ondemand src and enable access/execute for scripts and html
ENV ONDEMAND_HOME /home/ondemand
ADD . ${ONDEMAND_HOME}
RUN chmod -R 755 ${ONDEMAND_HOME}

# configure mod_visus and webviewer
COPY conf/ondemand.conf /etc/apache2/sites-enabled/000-default.conf
#COPY resources/shared/visus.config ${VISUS_HOME}  (or symlink; and note this is currently mapped in kubernetes/visus-ondemand.yaml)

# web root is ${VISUS_HOME}/webviewer, so symlink ondemand there to make ondemand/ondemand.php accessible
#<ctc> - copy to /home/ondemand or ${VISUS_HOME}/ondemand... don't want to symlink to webviewer.
#      - modify 000-default.conf or add another one if necessary (prolly add one)
#RUN ln -s ${ONDEMAND_HOME} ${VISUS_HOME}/webviewer/ondemand (see the ondemand.conf above that replaced OpenVisus' version)

# link cgi scripts and configuration to cgi-bin (TODO: is this somehow avoidable?)
#<ctc> symlinking these filesworked, but on some restart it stopped, so they have to be copied instead. Meh.
#<ctc> I'd rather they stay in ondemand in the first place, so just figure this out (give ondemand it's own apache .conf with appropriate perms)
# RUN cp ${ONDEMAND_HOME}/cgi/cdat_to_idx_create.cgi /usr/lib/cgi-bin/ && \
#     cp ${ONDEMAND_HOME}/cgi/datasize.cgi /usr/lib/cgi-bin/ && \
#     cp ${ONDEMAND_HOME}/conf/ondemand-cfg.sh /usr/lib/cgi-bin/

CMD "${ONDEMAND_HOME}/bin/start_service.sh"
