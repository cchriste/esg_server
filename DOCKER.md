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

Configure it by modifying conf/ondemand-cfg.sh with any necessary changes, for example:
```
ONDEMAND_HOST=https://aims2.llnl.gov/visus
UVCDAT_DIR="/usr/local/uvcdat/2.2.0"
ONDEMAND_PORT=42299
ONDEMAND_XMLPATH="/data/xml"
ONDEMAND_IDXPATH="/data/idx"
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

## Running with Kubernetes

Some servers require the use of Kubernetes pods to run docker containers. There is a visus-ondemand.yaml example in the kubernetes directory that can be modified and run with a command like:
```
kubectl apply -f visus-ondemand.yaml
```
This command can also be used if the .yaml file or Docker image is updated. Other useful commands include:
```
VISUS_POD=$(kubectl get pods | grep visus | tr -s " " | cut -d " " -f 1)
kubectl logs $VISUS_POD
kubectl exec -it $VISUS_POD /bin/bash"
kubectl delete -f visus-ondemand.yaml
```
