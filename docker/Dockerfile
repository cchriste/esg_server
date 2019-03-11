#
# ViSUS OnDemand Dockerfile
#
# NOTE: build from parent directory:
#  `docker build -t ondemand -f docker/Dockerfile .`

# Installation based on visus/anaconda, which has OpenVisus w/ python, webviewer, and apache mod_visus
# NOTE: - includes Docker ENVs for VISUS_HOME and CONDA_PREFIX
#       - both conda update and apt-get update have been run in the (presumably recent) the parent image
FROM visus/anaconda




#(try these by hand to see if it's all really needed: numpy, libgomp1, a2enmod cgid, cdms2, genutil, lxml, libxml2-dev...)
RUN apt-get install -y libgomp1
  #these may also be necessary:
  # cmake swig bzip2 ca-certificates curl build-essential
RUN conda install -y numpy

# enable CGI
RUN a2enmod cgid

# install conda packages
RUN conda install -c conda-forge cdms2 && \
    conda install -c conda-forge genutil && \
    conda install -c conda-forge lxml

# # install libxml2
# RUN apt-get install -y libxml2-dev python-dev libapache2-mod-php




# Install ondemand
#[] can these files be symlinked?
#[] Not sure about all the copying. At the least, let's use an install script.
#[] install script should set cfg params in respective files

ENV ONDEMAND_HOME $VISUS_HOME/ondemand

# clone ondemand
ENV ONDEMAND_HOME $VISUS_HOME/ondemand
ADD https://api.github.com/repos/sci-visus/ondemand/git/refs/heads/master version.json
RUN git clone -bmaster https://github.com/sci-visus/ondemand.git $ONDEMAND_HOME

# # web root is $VISUS_HOME/webviewer, so symlink ondemand there to make ondemand/ondemand.php accessible
# RUN ln -s $ONDEMAND_HOME $VISUS_HOME/webviewer/ondemand

# # copy cgi scripts to cgi-bin
RUN cp $ONDEMAND_HOME/cgi/cdat_to_idx_create.cgi /usr/lib/cgi-bin/ && \
    cp $ONDEMAND_HOME/cgi/datasize.cgi /usr/lib/cgi-bin/

# # NOTE: if copying the .cgi scripts then map ondemand-cfg.sh to both these directories
# #    cp $ONDEMAND_HOME/conf/ondemand-cfg.sh.template /usr/lib/cgi-bin/ && \
# #    cp $ONDEMAND_HOME/conf/ondemand-cfg.sh.template $ONDEMAND_HOME/conf/ondemand-cfg.sh




WORKDIR $ONDEMAND_HOME/code
EXPOSE 42299

CMD ["/home/visus/ondemand/code/start_service.sh"]
