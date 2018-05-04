Docker container with ViSUS, Miniconda and On-demand conversion service
-----------------------------------

```
cd <path/to/directory/containing/this/file>
On Windows:
pushd ..\code
dos2unix *.sh # fix git problem
popd
pushd ..\conf 
dos2unix *.sh # fix git problem
popd

tar --directory=../ -c -z -f ondemand.tar.gz code conf cgi docs html media

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
docker run -it --rm -p 80:80 -p 42299:42299 -v <path_to_xml>:/data/xml -v <path_to_idx>:/data/idx -v <path_to_config> /visus/config ondemand
```

in another shell you can test it:
```
curl -v "http://$(docker-machine ip):80/mod_visus?action=list"
curl -v "http://$(docker-machine ip):42299/create?{dataset=$(dataset_name)}"
```