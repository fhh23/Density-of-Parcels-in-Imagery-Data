# Density-of-Parcels-in-Imagery-Data

## Outline

1. [Problem Overview](README.md#1-problem-overview)
2. [Setup](README.md#2-setup)
3. [Data Exploration and Ingestion](README.md#3-data-exploration-and-ingestion)
4. [Queries](README.md#4-queries)
5. [Python Script](README.md#5-python-script)
6. [Performance](README.md#6-performance)



## 1. Problem Overview

Given imagery data in the form of a multi-level raster tile map, at a resolution of 20 the geometries and centroids of all detected parcels are saved and stored as a seperate vector layer. The task is to write a pipeline to calculate the density of these parcels in two different contexts:

* With respect to a set of tiles at any desired zoom level between 16 and 20
* With respect to a human-readable map and associated boundaries of interest (e.g. political or metropolitan boundaries)


## 2. Setup

Install Postgres and PostGIS package.
Install QGIS.
Install Python3


## 3. Data Exploration and Ingestion

<img align="left" src="pics/stream_pipeline.JPG" />


There are 3 different suggested souces of data to use. The first is publicly available shapefiles of state geometries [[1]]. The second is publicly available census data to use as proxies [[2]]. The third is a tile map system containing parcel information provided by Cape Analytics.

First I imported the shapefiles of the state geometries and Cape Analytics tile map system into QGIS to visualize the distribution of parcels and make sure I was using the correct data. I used the 500k resolution files for the state geometries.

<img src="pics/Overlay1.PNG" />

Next, I was unsure of what the public census data was to be used for and so I imported it as a raster layer in QGIS and compared it with the Cape Analytics data. From the images below, I inferred that the Cape Analytics data was simply a subset of this census data which was converted to a shapefile. Therefore, I did not include the public census data in my database, instead choosing to limit the scope of parcel density to the following states: TN, KY, VA, NC, GA, AL, MS, AR, MO, IL.

<img src="pics/Parcels1.PNG" width="425"/> <img src="pics/Parcels2.PNG" width="425"/> 

Since my data was already in QGIS, I used QGIS to import my data into Postgres [[3]]. So I had 2 tables in Postgres, one for the states geometries and one for the tile map system. In PostGIS, I ran a simple query to see what the columns and data looked like.

States Table:
<img src="pics/States_Table_analyze.PNG" />

Tiles Table:
<img src="pics/Tiles_Table_analyze.PNG" />

I also wanted to take a closer look at the geometry columns for both tables, so I ran the query below. 

<img src="pics/SRID.PNG" />

What I found was that the spatial reference identifier for the two geometries was different. Since my initial intuition was that I would need to do a spatial join between these two geometries, I created a new geometry column in the tiles table with the tile geometry SRID converted.

<img src="pics/CREATE_COL_tiles.PNG" />

## 4. Queries



## 5. Python Script


## 6. Further Considerations



[1]: https://www.census.gov/geo/maps-data/data/cbf/cbf_state.html
[2]: http://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-count
[3]: http://stackoverflow.com/questions/40636158/import-shape-file-into-postgis-with-pgadmin-4
