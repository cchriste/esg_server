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