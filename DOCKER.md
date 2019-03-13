On-demand Docker container built on OpenVisus (visus/anaconda)
-------------------------------------------------------------------------------

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

Configure it by modifying conf/ondemand-env.sh with any necessary changes, for example:
```
ONDEMAND_HOST=https://aims2.llnl.gov/visus
UVCDAT_DIR="/usr/local/uvcdat/2.2.0"
```

Run it:
```
export VISUS_HOME=/home/OpenVisus
docker run -it --rm -p 80:80 -p 42299:42299 -v <local_xml_path>:/data/xml -v <local_idx_path>:/data/idx -v <local_visus.config> ${VISUS_HOME}/visus.config ondemand
```

in another shell you can test it:
```
curl -v "http://localhost/mod_visus?action=list"
curl -v "http://localhost/cgi-bin/cdat_to_idx_create.cgi?dataset=$(dataset_name)"
```
