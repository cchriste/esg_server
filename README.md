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
Overview
--------------------------------------
The IDX Stream on-demand data converter is designed to provide streaming hierarchical versions of equivalent NetCDF climate data volumes in a user-directed manner such that specific timestep fields are converted just-in-time. Providing volumes in the IDX format, an efficient hierarchical layout based on data reordering, permits the bulk of the data to remain on the server and facilitates interactive analysis and visualization by immediately sending results for specific data requests. Initial conversions are cached, amortizing the cost of future requests. This method of data access is especially important for large domain data.

This document describes the system beginning with the motivation of data reordering as an efficient mechanism to facilitate coarse-to-fine streaming access, continuing with pertinent implementation details and an overview of using the system. The reader is encouraged to look directly to the code for more specific information. Detailed installation instructions can be found in **INSTALL.md**.

--------------------------------------
IDX Data Reordering
--------------------------------------
As implied by its name, data reordering simply changes the layout of data on disk (or in memory) to efficiently facilitate operations such as downsampling and subregion queries. Thus, the size of the data on disk remains similar to the original data. [This image](media/figures/idx_compare.png) illustrates the comparison between traditional image layout and the hierarchical layout of IDX. The mechanism of data reordering utilized by the IDX format is [visualized](media/figures/idx_layout0.png) [in](media/figures/idx_layout1.png) [this](media/figures/idx_layout2.png) [sequence](media/figures/idx_layout3.png) [of](media/figures/idx_layout4.png) [images](media/figures/idx_layout5.png). More details about IDX can be found at <http://github.com/sci-visus/nvisusio/wiki>.

Data reordering facilitates more rapid, dynamic analysis and visualization by enabling coarse-to-fine resolution loading of view-dependent regions of large multidimensional datasets. Reordering allows data sizes to remain constant while providing fast access to coarse resolution levels and subregions of interest. Reordering can be done on-the-fly, or during data generation. *The finest resolution is identical to the original data, so there is no loss of data fidelity.* Furthermore, coarse resolution levels support both spatial and temporal filtering so certain guarantees can be added, such as max/min/avg for a given coarse resolution sample.

--------------------------------------
ViSUS IDX Data Server
--------------------------------------
Once data is reordered into the IDX data format, it can be streamed in a coarse-to-fine fashion to users with IDX-compatible clients. The ViSUS IDX Data Server is an apache plugin that responds to requests for given regions of data at a specified resolution level. The client connection to the server is stateless: individual http requests contain all the necessary information to describe the dataset and desired region of interest to be retrieved.

The ViSUS Data Server can be downloaded from <http://atlantis.sci.utah.edu/builds/ViSUS> and installed independently or in association with an ESGF data node. The server must have access to the cache of converted climate data.

--------------------------------------
On-demand Conversion Overview
--------------------------------------
[This figure](media/esg_server_overview.pdf) shows the design of the overall system. Beginning at the ESGF search page (top-left of the diagram), the user can download an xml configuration file describing how to load the selected climate dataset. When the user selects a dataset its corresponding IDX metadata is created and registered with an associated ViSUS data server. This configuration will contain references to the multiple volumes that are part of the same climate model. The data can be loaded in a ViSUS client or compatible component. Available datasets can also be listed directly from the associated server.

	Once the user has the URL the dataset can be opened from any IDX-compatible client, such as UV-CDAT (top-right). Its hierarchical nature allows coarse resolution data to be streamed very quickly, providing a preview of the final data and facilitating interactivity. When data is requested, a remote query is made to the ViSUS server, which checks if the data already exists in the cache. If so, it sends the cached data immediately. Otherwise, it calls the climate data converter service which converts the data and returns. After conversion the data is available in the cache so successive attempts to access the data will succeed without incurring additional conversion costs.

--------------------------------------
Using the ViSUS Framework in an external application 
--------------------------------------
It is simple to instrument your own application to read local or remote IDX data.

Please see docs/examples/external_nvisusio in the downloaded ViSUS library at <http://atlantis.sci.utah.edu/builds/ViSUS>.
