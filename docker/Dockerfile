FROM visus/miniconda

# enable CGI
RUN a2enmod cgid

# install conda packages
RUN conda install -c conda-forge cdms2 && \
    conda install -c conda-forge genutil && \
    conda install -c conda-forge lxml

# clone ondemand
ENV ONDEMAND_HOME $VISUS_HOME/ondemand
RUN git clone https://github.com/sci-visus/ondemand $ONDEMAND_HOME   

# configure webviewer
ADD config.js   $VISUS_HOME/webviewer

# copy cgi scripts to cgi-bin
RUN cp $ONDEMAND_HOME/cgi/cdat_to_idx_create.cgi /usr/lib/cgi-bin/ && \
    cp $ONDEMAND_HOME/cgi/datasize.cgi /usr/lib/cgi-bin/

WORKDIR $ONDEMAND_HOME/code
EXPOSE 42299

CMD ["/home/visus/ondemand/code/start_service.sh"]