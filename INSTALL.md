-----------------------------------------------
IDX Stream On-Demand Data Converter
===============================================
-----------------------------------------------

| IDX Stream On-Demand Data Converter
| Copyright (c) 2010-2016 University of Utah  
| Scientific Computing and Imaging Institute  
| 72 S Central Campus Drive, Room 3750  
| Salt Lake City, UT 84112  
|  
| **PLEASE NOTE:** *We have not finalized the license for this product. The  
| following describes the most restrictive Creative Commons license, but this will  
| likely be changed once the final product is released. Please contact us in the  
| meantime if you would like to use or modify this system.*  
|  
| IDX Stream is licensed under the Creative Commons  
| Attribution-NonCommercial-NoDerivatives 4.0  
| International License. See **LICENSE.md**.  
|  
| For information about this project see:  
| <http://www.cedmav.com>  
| or contact: <pascucci@sci.utah.edu>  
| For support: <IDXStream-support@sci.utah.edu>  

--------------------------------------
Quick Start
--------------------------------------
Make a copy of conf/ondemand-env.sh.template as conf/ondemand-env.sh and modify it according to your local setup. There are some examples for other systems available. This entails deciding where to place the converted data, how big of a maximum cache size to enforce, and where to find the associated IDX Server.

Change to the destination xml path (ONDEMAND_XMLPATH from the ondemand-env.sh file above) and run <path_to_ondemand>/code/start_service.sh.

The service should be started! Follow the log file for details and troubleshooting.

--------------------------------------
Adding a Cron Job to maage the cache
--------------------------------------
There is a script to maintain the cache size that should be executed periodically using *cron*. The script can be found in code/cleanup_lru.sh.

--------------------------------------
Starting the IDX Data Server
--------------------------------------
Please see the instructions in the nvisusio server deployment to install the IDX Data Server.
