# Visualizer technologies choice


### Newer version

- Gets all 8 adjacent tiles from the 1 center tile, where the vehicle coordinates are. The background is composed by the 9 tiles. (768x768)
    - Uses a tile cache for storing the tiles in use, only downloading from the OSM API the new tiles necessary that are not present in cache.

- Formulas used to convert lat and lon to the correct pixel in the tile. (This finding of the position is done accordingly to the center tile, annd that's why everything on this is multiplied by 256 and not 768)

- So what are these lat and lon objects printed on top of the map? The results of the simulation are the lines (representing future trajectories of the vehicles, using MCMs) and the points are the path history drawn independently from the simulation and from CAMs.


### Older version of the visualizer...
I will be using WebSockets since it maintains a persistent connection, unlike HTTP, which requires a new request for every server response;

Will also be using FastAPI over Node JS for example, because the agent code is already written in Python so for better interoperability that is the choice;

The API will be RESTful because i need multiple endpoints to distinguish information!? GraphQL API uses flexible queries, single query for multiple resources (using only 1 endpoint), does fewer requests and so is more efficient!?

I will be using JavaScript/React!? for the frontend part. React lets make the reusage of other code, while simple JS does not feature that.

Map -> leaflet?