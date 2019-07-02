#
# ViSUS OnDemand Dockerfile
#

# Installation based on visus/anaconda, which has OpenVisus w/ python, webviewer, and apache mod_visus
# NOTE: - includes Docker ENVs for VISUS_HOME and CONDA_PREFIX
#       - both conda update and apt-get update have been run in the parent image
#       - for official releases, set a specific tag (e.g., visus/anaconda:1.3.8)
FROM visus/anaconda
#1.3.8-newest_webviewer

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
# # install libxml2 (if necessary for cdat_to_idx to work)
# RUN apt-get install -y libxml2-dev python-dev libapache2-mod-php

# Update webviewer
RUN cd ${VISUS_HOME}/webviewer && git pull
 
# Install ondemand #
# add ondemand src and enable access/execute for scripts and html
ENV ONDEMAND_HOME /home/ondemand
ADD . ${ONDEMAND_HOME}
RUN chgrp -R www-data ${ONDEMAND_HOME}
RUN chmod -R 775 ${ONDEMAND_HOME}
RUN chgrp -R www-data ${VISUS_HOME}/
RUN chmod -R 775 ${VISUS_HOME}/

# configure mod_visus and webviewer
COPY conf/ondemand.conf /etc/apache2/sites-enabled/000-default.conf
#COPY resources/shared/visus.config ${VISUS_HOME}  (or symlink; and note this is currently mapped in kubernetes/visus-ondemand.yaml)

CMD "${ONDEMAND_HOME}/bin/start_service.sh"
