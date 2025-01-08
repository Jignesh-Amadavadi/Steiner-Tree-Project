import networkx as nx
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import unary_union
import matplotlib.pyplot as plt
import math
import random
from itertools import combinations

# Define building footprints as polygons
buildings = [
    Polygon([(3, 3), (6, 3), (6, 6), (3, 6)]),  # Simple rectangle building
    Polygon([(8, 1), (9, 1), (9.5, 2), (10, 4), (8, 4)]),  # Irregular pentagon building
    Polygon([(1, 8), (2, 7), (3, 9), (1.5, 9)])  # Triangle building
]

# Define the map's bounding box and subtract building footprints
bounding_box = Polygon([(0, 0), (12, 0), (12, 10), (0, 10)])  # Entire map boundary
combined_buildings = unary_union(buildings)  # Combine all buildings into a single geometry
free_space = bounding_box.difference(combined_buildings)  # Subtract combined buildings

# Generate random restroom polygons
def generate_random_restroom_polygons(free_space, num_restrooms):
    restrooms = []
    while len(restrooms) < num_restrooms:
        x, y = random.uniform(0, 12), random.uniform(0, 10)
        restroom = Polygon([(x, y), (x + 0.5, y), (x + 0.5, y + 0.5), (x, y + 0.5)])
        if free_space.contains(restroom):
            restrooms.append(restroom)
    return restrooms

# Add predefined restrooms
restrooms = [
    Polygon([(1, 1), (1.5, 1), (1.5, 1.5), (1, 1.5)]),  # Predefined restroom R1
    Polygon([(7, 7), (7.5, 7), (7.5, 7.5), (7, 7.5)])   # Predefined restroom R2
]
restrooms += generate_random_restroom_polygons(free_space, 10)

# Extract Steiner points (corners of buildings)
steiner_points = []
for building in buildings:
    steiner_points.extend(list(building.exterior.coords))
steiner_points = [Point(coord) for coord in steiner_points]

# Function to calculate Euclidean distance between two points
def euclidean_distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

# Function to check if a line segment between two points intersects any building
def is_valid_path(p1, p2, buildings):
    line = LineString([p1, p2])
    for building in buildings:
        if line.intersects(building) and not line.touches(building):
            return False
    return True

# Step 1: Construct a complete graph with restrooms and Steiner points
graph = nx.Graph()

# Add edges between restrooms and Steiner points
for restroom in restrooms:
    for steiner_point in steiner_points:
        if is_valid_path(restroom.centroid, steiner_point, buildings):
            distance = euclidean_distance(restroom.centroid, steiner_point)
            graph.add_edge(restroom.centroid, steiner_point, weight=distance)

# Add edges between Steiner points
for p1, p2 in combinations(steiner_points, 2):
    if is_valid_path(p1, p2, buildings):
        distance = euclidean_distance(p1, p2)
        graph.add_edge(p1, p2, weight=distance)

# Add edges between restrooms if valid
for r1, r2 in combinations(restrooms, 2):
    if is_valid_path(r1.centroid, r2.centroid, buildings):
        distance = euclidean_distance(r1.centroid, r2.centroid)
        graph.add_edge(r1.centroid, r2.centroid, weight=distance)

# Step 2: Approximation algorithm for Steiner tree
# Find the shortest paths between all terminal nodes (restrooms)
terminal_nodes = [restroom.centroid for restroom in restrooms]
complete_graph = nx.Graph()

for u, v in combinations(terminal_nodes, 2):
    try:
        shortest_path = nx.shortest_path(graph, source=u, target=v, weight="weight")
        path_length = sum(euclidean_distance(shortest_path[i], shortest_path[i + 1])
                          for i in range(len(shortest_path) - 1))
        complete_graph.add_edge(u, v, weight=path_length)
    except nx.NetworkXNoPath:
        pass  # Skip if no valid path exists

# Step 3: Minimum Spanning Tree (MST)
mst = nx.minimum_spanning_tree(complete_graph)

# Replace MST edges with actual paths in the original graph
final_edges = []
for u, v, data in mst.edges(data=True):
    shortest_path = nx.shortest_path(graph, source=u, target=v, weight="weight")
    final_edges.extend(zip(shortest_path[:-1], shortest_path[1:]))

# Plot the results
plt.figure(figsize=(12, 12))

# Plot restrooms
for i, restroom in enumerate(restrooms):
    x, y = restroom.exterior.xy
    plt.fill(x, y, color="blue", alpha=0.6)  # Blue polygons for restrooms
    plt.text(restroom.centroid.x, restroom.centroid.y, f"R{i+1}", fontsize=10, ha='center')

# Plot buildings
for building in buildings:
    x, y = building.exterior.xy
    plt.fill(x, y, color="gray", alpha=0.5)  # Gray color for buildings

# Plot Steiner points
for steiner_point in steiner_points:
    plt.plot(steiner_point.x, steiner_point.y, 'ro', markersize=5)  # Red dots for Steiner points

# Plot edges in the Steiner tree
for u, v in final_edges:
    plt.plot([u.x, v.x], [u.y, v.y], 'g-', linewidth=2)  # Green lines for Steiner tree

# Add labels and title
plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")
plt.title("Restroom Connections with Steiner Points (2-Approximation)")
plt.grid(True)
plt.show()
