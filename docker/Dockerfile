FROM visus-anaconda

RUN conda install -c conda-forge cdms2 && \
    conda install -c conda-forge genutil && \
    conda install -c conda-forge lxml
    
#RUN curl https://codeload.github.com/sci-visus/ondemand/zip/porting-to-new-visus -o master.zip \
#    && unzip master.zip \
#    && rm master.zip \
#    && mv ondemand-porting-to-new-visus ondemand

ADD ondemand.tar.gz /visus/ondemand
RUN cp /visus/ondemand/cgi/cdat_to_idx_create.cgi /usr/lib/cgi-bin/ && \
    cp /visus/ondemand/cgi/datasize.cgi /usr/lib/cgi-bin/

WORKDIR /visus/ondemand/code
EXPOSE 42299

CMD ["/visus/ondemand/code/start_service.sh"]