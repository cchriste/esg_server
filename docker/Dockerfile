FROM visus/miniconda

# enable CGI
RUN a2enmod cgid

# install conda packages
RUN conda install -c conda-forge cdms2 && \
    conda install -c conda-forge genutil && \
    conda install -c conda-forge lxml

# install libxml2
RUN apt-get update
RUN apt-get install -y libxml2-dev python-dev libapache2-mod-php

# clone XIDX
ENV XIDX_HOME $VISUS_HOME/XIDX 
RUN git clone https://github.com/sci-visus/XIDX.git $XIDX_HOME
WORKDIR $XIDX_HOME
RUN mkdir -p build
WORKDIR $XIDX_HOME/build
RUN cmake .. && make 
ENV PYTHONPATH $XIDX_HOME/build:$PYTHONPATH

# clone ondemand
ENV ONDEMAND_HOME $VISUS_HOME/ondemand
RUN git clone https://github.com/sci-visus/ondemand $ONDEMAND_HOME   

# install webviewer
RUN rm -R $VISUS_HOME/webviewer
RUN git clone https://github.com/sci-visus/visus_javascript $VISUS_HOME/webviewer

# configure webviewer
ADD config.js   $VISUS_HOME/webviewer

# copy cgi scripts to cgi-bin
RUN cp $ONDEMAND_HOME/cgi/cdat_to_idx_create.cgi /usr/lib/cgi-bin/ && \
    cp $ONDEMAND_HOME/cgi/datasize.cgi /usr/lib/cgi-bin/

WORKDIR $ONDEMAND_HOME/code
EXPOSE 42299

CMD ["/home/visus/ondemand/code/start_service.sh"]