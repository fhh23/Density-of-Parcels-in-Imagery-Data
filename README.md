# Density-of-Parcels-in-Imagery-Data

## Outline

1. [Problem Overview](README.md#1-problem-overview)
2. [Setup](README.md#2-setup)
3. [Data Exploration and Ingestion](README.md#3-data-exploration-and-ingestion)
4. [Queries](README.md#4-queries)
5. [Python Script](README.md#5-python-script)
6. [Results and Further Considerations](README.md#6-results-and-further-considerations)



## 1. Problem Overview

Given imagery data in the form of a multi-level raster tile map, at a resolution of 20 the geometries and centroids of all detected parcels are saved and stored as a seperate vector layer. The task is to implement a pipeline to calculate the density of these parcels in two different contexts:

* With respect to a set of tiles at any desired zoom level between 16 and 20
* With respect to a human-readable map and associated boundaries of interest (e.g. political or metropolitan boundaries)

At a high level, in order to solve this problem I did a spatial join between the geometries of parcels and the geometry of the state of interest in a certain map view. In order to speed up this spatial join, I created an index on the tile map system geometries.

## 2. Setup

I used the following tools:

* Latest version of Postgres and PostGIS package.
* Latest version of QGIS.
* Python3


## 3. Data Exploration and Ingestion

There are 3 different suggested souces of data to use. The first is publicly available shapefiles of state geometries [[1]]. The second is publicly available census data to use as proxies [[2]]. The third is a tile map system containing parcel information provided by Cape Analytics.

First I imported the shapefiles of the state geometries and Cape Analytics tile map system into QGIS to visualize the distribution of parcels and make sure I was using the correct data. I used the 500k resolution files for the state geometries.

<img src="pics/Overlay1.PNG" />

Next, I was unsure of what the public census data was to be used for, so I imported it as a raster layer in QGIS and compared it with the Cape Analytics data. From the images below, I inferred that the Cape Analytics data was simply a subset of this census data which was converted to a shapefile. Therefore, I did not include the public census data in my database, instead choosing to limit the scope of parcel density to the following states: TN, KY, VA, NC, GA, AL, MS, AR, MO, IL.

<img src="pics/Parcels1.PNG" width="425"/> <img src="pics/Parcels2.PNG" width="425"/> 

Since my data was already in QGIS, I used QGIS to import my data into Postgres [[3]]. So I had 2 tables in Postgres, one for the states geometries and one for the tile map system. In PostGIS, I ran a simple query to see what the columns and data looked like.

States Table:
```sql
SELECT * FROM public.states_500k
ORDER BY id ASC LIMIT 100
```
<img src="pics/States_Table_analyze.PNG" />

Tiles Table:
```sql
SELECT * FROM public.states_500k
ORDER BY id ASC LIMIT 100
```
<img src="pics/Tiles_Table_analyze.PNG" />

I also wanted to take a closer look at the geometry columns for both tables, so I ran the query below. 


```sql
SELECT ST_SRID(tiles.geom), ST_SRID(states.geom)
FROM public.tiles as tiles, public.states_500k as states
LIMIT 1
```
<img src="pics/SRID_query.PNG" />

What I found was that the spatial reference identifier for the two geometries was different. Since my initial intuition was that I would need to do a spatial join between these two geometries, I created a new geometry column in the tiles table with the tile geometry SRID converted.

```sql
ALTER TABLE public.tiles ADD COLUMN geom_conv geometry(Geometry, 4269);
UPDATE public.tiles SET geom_conv = ST_TRANSFORM(geom, 4269);
```

## 4. Queries

Before I started implementing queries, I had to think about how I was going to test my query. More specifically, how was I going to know what area of the map the user was looking at so that I could find the parcel density in that area. I decided to make the following assumption: if the user was looking at a map at a certain zoom level (we will call this the map view), the coordinates of the map view boundary would be passed to my pipeline. In addition, the user would specify what state they are currently interested in finding the parcel density for (this handles the case where there are multiple states in the map view).

So first I start with the query to generate a geometry from the user's map view. This was my initial approach:
```sql
SELECT ST_MakePolygon(ST_AddPoint(view.open_line, ST_StartPoint(view.open_line))) as user_geom
FROM ( 
  SELECT ST_GeomFromText('LINESTRING(-89.98 37.79, -89.8 37.79, -89.78 37.66, -89.96 37.66)', 4269) as open_line
  ) as view
```

However, I found that if my coordinates (which I was manually entering) weren't perfect or if I had selected a linestring which crossed over multiple states, I ran into issues. After more research, I found the ST_MakeEnvelope function, which created a bounding box from coordinates.
```sql
SELECT ST_makeenvelope(-89.5282, 37.3087, -89.4805, 37.3585,4269) as geom
```

Next I wrote a query to get the geometry of the state the user is interested in. Just as an example, I have assumed the user has chosen Missouri.
```sql
SELECT name, geom 
FROM public.states_500k 
WHERE name like 'Missouri'
```

Now that I have these 2 geometries, I find the intersection of them. This ensures that if the user's map view spans multiple states, the geometry is restricted only to the state of interest.
``` sql
SELECT ST_Intersection(state.geom, box.geom) as geom
        FROM
		(SELECT geom from public.states_500k where name like 'Missouri') as state,
		(SELECT ST_makeenvelope(-89.5282, 37.3087, -89.4805, 37.3585,4269) as geom) as box
```

Finally, I find where this new bounding box intersects the parcels. This will return the total number of parcels in the bounding box area. This is important because this is what I used to validate my answer in QGIS (discussed in section 4.1). 
```sql
SELECT * 
FROM public.tiles as parcels, 
	(SELECT ST_Intersection(state.geom, box.geom) as geom
        FROM
		(SELECT geom from public.states_500k where name like 'Missouri') as state,
		(SELECT ST_makeenvelope(-89.5282, 37.3087, -89.4805, 37.3585,4269) as geom) as box) as boundary
WHERE ST_Intersects(parcels.geom_conv, boundary.geom)
```

The below query is the complete one to return the density in parcels per square mile.
```sql
SELECT COUNT(*)/AVG(boundary.area) as density
FROM public.tiles as parcels, 
	(SELECT ST_Intersection(state.geom, box.geom) as geom, ST_AREA(ST_Intersection(state.geom, box.geom)::geography)/1609.34^2  as area
        FROM
		(SELECT geom from public.states_500k where name like 'Missouri') as state,
		(SELECT ST_makeenvelope(-89.5282, 37.3087, -89.4805, 37.3585,4269) as geom) as box) as boundary
WHERE ST_Intersects(parcels.geom_conv, boundary.geom)
```

In order to speed up the query, an index was created in the tiles table for the converted geometry column. This allows for more efficient lookup when doing the spatial join.
``` sql
CREATE INDEX geom_idx ON public.tiles USING GIST (geom_conv);
ANALYZE public.tiles;
CLUSTER public.tiles USING geom_idx;
VACUUM ANALYZE public.tiles;
```

### 4.1 Validating Results

In order to validate the query's accuracy, I ran the spatial query in QGIS and ran the same query in Postgres (with the coordinates manually entered) and compared the parcel ids in the results. Note that the ids in QGIS are one less than the ids in Postgres. One of the queries which was done on the boundary of two states is shown below.

QGIS results:
<img src="pics/QGIS_query_results.PNG" />

Postgres results:
<img src="pics/Postgres_query_results.PNG" />

## 5. Python Script

A minimal python script was written just to connect to my local Postgres instance, make a query, and print the density as a result. With further time, this would allow for a user input of coordinates for the map view and state of interest, and functions to zoom in and out of the map (rather than enter new coordinates each time). Also, database login info would be moved to a configuration file.

## 6. Results and Further Considerations

In order to solve this problem I did a spatial join between the geometries of parcels and the geometry of the state of interest in a certain map view. In order to speed up this spatial join, I created an index on the tile map system geometries. An index helps because instead of looping through every element in the parcels table during a join sequentially, the query will instead loop through elements based on geometries that are next to each other. A GiST (Generalized Search Trees) index was used, as this is a natural way of grouping map tiles with a 2D relation to each other. Making sure the index was actually being used was a challenge, and the approach which worked best was to "flatten" the query as much as possible so the ST_Intersects call wasn't nested.

There are some areas of potential further improvement. 
1. The ST_Intersection call between the map view bounding box and the state geometry is slow. Case statements to quickly resolve the case where the bounding box is completely within or completely outside the state could speed this up. 
2. The state geometries are made up of many polygon. Creating a new table with the results of ST_Dump on these multipolygons could make finding the intersection with the map view bounding box faster. Making an index on this new table geometry could also speed up the spatial join with the parcels geometry.
3. There are various timing logs and graphical interfaces which give insight into how your program is running. With more time I would have used them to have a more detailed runtime analysis of different queries I tried. However, I did use the "explain" functionality  to analyze when my index was and wasn't being used. Below is the graphical explanation of my final query. Hovering over the blocks in Postgres shows that the states table used a sequential scan, and the tiles table used a bitmap heap scan.

<img src="pics/Explain_Graph.PNG" />

There are also considerations to consider when scaling this solution up to a distributed database. First, tile and state data should be partitioned by geometry, so that geometries that are near each other are located on the same machine. Next, as the number of rows in the tables grows, the computation and memory cost of the indexes must be taken into account. This also includes parcels being added to the tiles table, as everytime this happends the index has to be recomputed. Caching is also an optimization that needs to be considered. When you zoom in and out of a level you are going to be looking at a lot of the same tiles, so having an LRU cache of tile geometries may help speed up subsequent queries.


[1]: https://www.census.gov/geo/maps-data/data/cbf/cbf_state.html
[2]: http://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-count
[3]: http://stackoverflow.com/questions/40636158/import-shape-file-into-postgis-with-pgadmin-4
