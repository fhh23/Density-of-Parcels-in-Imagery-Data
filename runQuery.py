#!/usr/bin/env python

import psycopg2

#DB connection properties
conn = psycopg2.connect(dbname = 'gisdb', host= 'localhost', port= 5432, user = 'postgres',password= 'pass')
cur = conn.cursor()  ## open a cursor


density_query = '''
SELECT COUNT(*)/AVG(boundary.area) as density
FROM public.tiles as parcels, 
	(SELECT ST_Intersection(state.geom, box.geom) as geom, ST_AREA(ST_Intersection(state.geom, box.geom)::geography)/1609.34^2  as area
        FROM
				(SELECT geom from public.states_500k where name like 'Missouri') as state,
				(SELECT ST_makeenvelope(-89.5282, 37.3087, -89.4805, 37.3585,4269) as geom) as box) as boundary
WHERE ST_Intersects(parcels.geom_conv, boundary.geom)
  '''
cur.execute(density_query)

for x in cur:
    print("Density per sq. mile:" + str(x[0]))

cur.close()
conn.close()