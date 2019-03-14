#
# ViSUS OnDemand Dockerfile
#

# Installation based on visus/anaconda, which has OpenVisus w/ python, webviewer, and apache mod_visus
# NOTE: - includes Docker ENVs for VISUS_HOME and CONDA_PREFIX
#       - both conda update and apt-get update have been run in the parent image
#       - for officially releases, set a specific tag (e.g., visus/anaconda:1.3.8)
FROM visus/anaconda:1.3.8




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
#[?] can these files be symlinked?
#[] Not sure about all the copying. At the least, let's use an install script.
#[] install script should set cfg params in respective files

ENV ONDEMAND_HOME ${VISUS_HOME}/ondemand
ADD . ${ONDEMAND_HOME}

# web root is ${VISUS_HOME}/webviewer, so symlink ondemand there to make ondemand/ondemand.php accessible
#<ctc> - copy to /home/ondemand or ${VISUS_HOME}/ondemand... don't want to symlink to webviewer.
#      - modify 000-default.conf or add another one if necessary (prolly add one)
RUN ln -s ${ONDEMAND_HOME} ${VISUS_HOME}/webviewer/ondemand

# link cgi scripts and configuration to cgi-bin (TODO: is this somehow avoidable?)
RUN ln -s ${ONDEMAND_HOME}/cgi/cdat_to_idx_create.cgi /usr/lib/cgi-bin/ && \
    ln -s ${ONDEMAND_HOME}/cgi/datasize.cgi /usr/lib/cgi-bin/ && \
    ln -s ${ONDEMAND_HOME}/conf/ondemand-cfg.sh /usr/lib/cgi-bin/


# EXPOSE 42299  #specified in ondemand-cfg.sh, and docker more-or-less ignores this anyway, so not necessary

CMD "${ONDEMAND_HOME}/bin/start_service.sh"
