# IDX Stream On-Demand Data Converter

| IDX Stream On-Demand Data Converter
| Copyright (c) 2010-2016 University of Utah  
| Scientific Computing and Imaging Institute  
| 72 S Central Campus Drive, Room 3750  
| Salt Lake City, UT 84112  

## Overview and quick start

Make a copy of conf/ondemand-cfg.sh.template, which contains all default, as conf/ondemand-cfg.sh and modify it according to your local setup. There are some examples for other systems available. This entails deciding where to place the converted data, how big of a maximum cache size to enforce, and where to find the associated IDX Server.

Change to the destination xml path (ONDEMAND_XMLPATH from the ondemand-cfg.sh file above) and run <path_to_ondemand>/code/start_service.sh.

The service should be started! Follow the log file for details and troubleshooting.


## Docker installation

See Docker/README.md for details.


## Specify data locations

The On-demand server requires access to the data desired to be streamed on demand, and the Docker version requires mapping these locations into the container on startup.

For the data which has been converted for streaming, a cache path is necessary. The size of this cache is specified explicitly in conf/ondemand-cfg.sh and the default value in conf/ondemand-cfg.sh.template will be used if it's not changed.


## Adding a Cron Job to manage the cache

There is a script to maintain the cache size that should be executed periodically using *cron*. The script can be found in code/cleanup_lru.sh.

A typical crontab entry might look like, to start daily at 02:15::

  15 2 * * * /export/christensen41/code/esg_server/code/cleanup_lru.sh

Here is the command to edit the crontab for a specific user::

  sudo crontab -u <user> -e

