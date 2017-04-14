# Density-of-Parcels-in-Imagery-Data

## Outline

1. [Problem Overview](README.md#1-problem-overview)
2. [Setup](README.md#2-setup)
3. [Analyzing the Data](README.md#3-analyzing-the-data)
 * 2.2 [Stream Processing and Data Storage](README.md#22-stream-processing-and-data-storage)
 * 2.3 [Batch Processing and Data Storage](README.md#23-batch-processing-and-data-storage)
 * 2.4 [UI Server](README.md#24-ui-server)
3. [Performance](README.md#3-performance)



## 1. Problem Overview

Given imagery data in the form of a multi-level raster tile map, at a resolution of 20 the geometries and centroids of all detected parcels are saved and stored as a seperate vector layer. The task is to write a pipeline to calculate the density of these parcels in two different contexts:

1. With respect to a set of tiles at any desired zoom level between 16 and 20
2. With respect to a human-readable map and associated boundaries of interest (e.g. political or metropolitan boundaries)


## 2. Setup

Install PostgreSQL and PostGIS package.
Install QGIS.
Install Python3


## 3. Analyzing the Data

There are 3 different suggested souces of data to use. The first is publicly available shapefiles of state geometries [1]. The second is publicly available census data to use as proxies 



## 4. Pipeline


### 4.1 Ingestion

### 4.2 Queries

### 4.3 Python Script


## 5. Further Considerations



[1]: https://www.census.gov/geo/maps-data/data/cbf/cbf_state.html
[2]: http://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-count
