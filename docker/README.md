Docker container with ViSUS, Miniconda and On-demand conversion service
-----------------------------------

Compile docker image:
```
docker build -t ondemand -f Dockerfile .
```

Commit image to dockerhub:
```
USER=<your dockerhub username>
docker tag ondemand $USER/ondemand
docker push $USER/ondemand
```

Run it:
```
docker run -it --rm -p 80:80 -p 42299:42299 -v <path_to_xml>:/data/xml -v <path_to_idx>:/data/idx -v <path_to_config/visus.config> /home/visus/visus.config -v <path_to_htpasswd/.htpasswd> /home/visus/.htpasswd ondemand
```

in another shell you can test it:
```
curl -v "http://$(docker-machine ip):80/mod_visus?action=list"
curl -v "http://$(docker-machine ip)/cgi-bin/cdat_to_idx_create.cgi?dataset=$(dataset_name)"
```

MUST do this the first time (or link to already extant visus.config):
cp docker/visus.config /data/data/idx/ondemand/visus.config

TODO: integrate this stuff into these instructions.
docker run -it -p 80:80 -p 42299:42299 \
  -v $PWD/nc:/data/xml -v $PWD/idx:/data/idx \
    -v $PWD/datasets:/home/visus/datasets/ \
      -v $PWD/viewer/config.js:/visus/webviewer/config.js \
        visus/ondemand

        where:
        - 42299 is the port we are using for the service that will create and convert a dataset (80 for the server)
          - /data/xml is the folder that should contain the .nc datasets
            - /data/idx is the folder that will contain the converted idx datasets

              The rest should be familiar to you. Of course you can map ports and folders to whatever you prefer.

              To request the creation of a new dataset (that will trigger the ondemand conversion when you try to visualize) you can use this HTT\
P request:
              http://localhost/cgi-bin/cdat_to_idx_create.cgi?dataset=ta_Amon_CESM1-WACCM_historical_r1i1p1_185001-200512.nc

              This request will look for that filename into the /data/xml folder that we mapped and create a corresponding idx file (so you can t\
ry with a small .nc dataset to start).
              Then this request will redirect you to the web viewer (localhost/viewer) where you should be able to see the first timestep being c\
onverted.



