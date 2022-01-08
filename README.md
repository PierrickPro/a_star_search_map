# A* Search Map

Generates a map, with vaccine centers (Vx), quarantine places (Qx) and playgrounds (Px). </br>
Each road has a different cost, depending on the locations arround.</br>
</br>
Using an A* heuristic search algorithm, the path with the lowest cost between any two points is calculated.</br>
The heuristic function is calculated using Manhattan distance.</br>
</br>
The networkx and matplotlib libraries were used to display the map.

## Rules

![alt text](https://github.com/PierrickPro/a_star_search_map/blob/main/empty_map.png?raw=true)

Edges are roads, cells are locations.</br>
</br>
Each location has a cost:</br>
Q = 0</br>
V = 2</br>
P = 3</br>
None = 1</br>

The cost of an edge between two locations is the average of the two locations.</br>
The cost of a border edge is the same as the cost of the location inside the box it closes.</br>

## Example

Start = O, Goal = U</br>
path found = ONMRQVU</br>
O: h = 6</br>
Total Cost =  7.0

![alt text](https://github.com/PierrickPro/a_star_search_map/blob/main/example.png?raw=true)
