#
# ViSUS OnDemand Dockerfile
#
# Must build this Docker image from parent directory (..):
#  `docker build -t ondemand -f docker/Dockerfile .`
# ...gonna just move this to the root path

# base this installation on visus/anaconda, which has OpenVisus w/ python, webviewer, and apache mod_visus
# NOTE: - includes Docker ENVs for VISUS_HOME and CONDA_PREFIX
#       - both conda update and apt-get update have been run in (presumably recent) the parent image
FROM visus/anaconda

#RUN apt-get install -y libgomp1
  #these may also be necessary:
  # cmake swig bzip2 ca-certificates curl build-essential
RUN conda install -y numpy

# RUN mkdir /root/visus
# RUN scp cam@gunship.sci.utah.edu:/tmp/install.tgz /root/visus
  # ^ this needs something to copy without permissions (or add an ssl cert, but that seems a security concern)
# RUN tar zcf /root/visus/install.tgz
# RUN rm /root/visus/install.tgz


#-----
#Also see Dockerfile.old:

# # enable CGI
# RUN a2enmod cgid

# # install conda packages
# RUN conda install -c conda-forge cdms2 && \
#     conda install -c conda-forge genutil && \
#     conda install -c conda-forge lxml

# # install libxml2
# RUN apt-get update
# RUN apt-get install -y libxml2-dev python-dev libapache2-mod-php

# # clone XIDX
# ENV XIDX_HOME $VISUS_HOME/XIDX 
# RUN git clone https://github.com/sci-visus/XIDX.git $XIDX_HOME
# WORKDIR $XIDX_HOME
# RUN mkdir -p build
# WORKDIR $XIDX_HOME/build
# RUN cmake .. && make 
# ENV PYTHONPATH $XIDX_HOME/build:$PYTHONPATH

# # install webviewer (it's already installed by visus/miniconda... but, it's broken, so that's why we're installing it again)
# RUN rm -R $VISUS_HOME/webviewer
# ADD https://api.github.com/repos/sci-visus/visus_javascript/git/refs/heads/master version.json
# RUN git clone -bmaster https://github.com/sci-visus/visus_javascript.git $VISUS_HOME/webviewer

# # install ondemand (that's where we are, so just copy it; enables development without git commits)
# ENV ONDEMAND_HOME $VISUS_HOME/ondemand
# ADD . $ONDEMAND_HOME

# # web root is $VISUS_HOME/webviewer, so symlink ondemand there to make ondemand/ondemand.php accessible
# RUN ln -s $ONDEMAND_HOME $VISUS_HOME/webviewer/ondemand

# # copy cgi scripts to cgi-bin
# RUN cp $ONDEMAND_HOME/cgi/cdat_to_idx_create.cgi /usr/lib/cgi-bin/ && \
#     cp $ONDEMAND_HOME/cgi/datasize.cgi /usr/lib/cgi-bin/

# # NOTE: if copying the .cgi scripts then map ondemand-cfg.sh to both these directories
# #    cp $ONDEMAND_HOME/conf/ondemand-cfg.sh.template /usr/lib/cgi-bin/ && \
# #    cp $ONDEMAND_HOME/conf/ondemand-cfg.sh.template $ONDEMAND_HOME/conf/ondemand-cfg.sh

# WORKDIR $ONDEMAND_HOME/code
# EXPOSE 42299

# CMD ["/home/visus/ondemand/code/start_service.sh"]
