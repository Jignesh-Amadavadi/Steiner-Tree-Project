import networkx as nx
from shapely.geometry import Point, Polygon, LineString, MultiPolygon, box
import matplotlib.pyplot as plt
import math
import random
from itertools import combinations

# Define building footprints as polygons
buildings = [
    Polygon([(3, 3), (6, 3), (6, 6), (3, 6)]),  # Simple rectangle
    Polygon([(8, 1), (9, 1), (9.5, 2), (10, 4), (8, 4)]),  # Irregular pentagon
    Polygon([(1, 8), (2, 7), (3, 9), (1.5, 9)])  # Triangle
]

# Define the map's bounding box and subtract building footprints
bounding_box = box(0, 0, 12, 10)  # Entire map boundary
free_space = bounding_box.difference(MultiPolygon(buildings))  # Subtract buildings

# Generate random restroom polygons
def generate_random_restroom_polygons(free_space, num_restrooms):
    restrooms = []
    while len(restrooms) < num_restrooms:
        # Generate a small rectangular restroom polygon
        x, y = random.uniform(0, 12), random.uniform(0, 10)
        restroom = Polygon([(x, y), (x + 0.5, y), (x + 0.5, y + 0.5), (x, y + 0.5)])
        if free_space.contains(restroom):
            restrooms.append(restroom)
    return restrooms

# Remove overlapping or too-close restrooms
def merge_close_restrooms(restrooms, threshold=1.0):
    filtered_restrooms = []
    for restroom in restrooms:
        if all(restroom.centroid.distance(other.centroid) > threshold for other in filtered_restrooms):
            filtered_restrooms.append(restroom)
    return filtered_restrooms

# Step 1: Generate and filter restrooms
restrooms = generate_random_restroom_polygons(free_space, 30)  # Generate more to allow filtering
restrooms = merge_close_restrooms(restrooms, threshold=1.0)  # Filter too-close restrooms

# Function to calculate Euclidean distance between the centroids of two polygons
def euclidean_distance(poly1, poly2):
    p1, p2 = poly1.centroid, poly2.centroid
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

# Function to check if a line segment between two polygons intersects any building
def is_valid_path(poly1, poly2, buildings, restrooms):
    line = LineString([poly1.centroid, poly2.centroid])
    for building in buildings:
        if line.intersects(building) and not line.touches(building):
            return False
    # Ensure it doesn't intersect other restroom polygons
    for restroom in restrooms:
        if restroom != poly1 and restroom != poly2 and line.intersects(restroom):
            return False
    return True

# Step 2: Create a complete graph with restroom polygons as nodes
G = nx.Graph()
for poly1, poly2 in combinations(restrooms, 2):  # Iterate over all pairs
    if is_valid_path(poly1, poly2, buildings, restrooms):  # Check if path is valid
        distance = euclidean_distance(poly1, poly2)
        G.add_edge(restrooms.index(poly1), restrooms.index(poly2), weight=distance)

# Step 3: Compute the Minimum Spanning Tree (MST) to connect all restrooms with minimal total length
mst = nx.minimum_spanning_tree(G)

# Step 4: Visualize the restrooms, buildings, and MST connections
plt.figure(figsize=(12, 12))

# Plot each restroom polygon
for i, restroom in enumerate(restrooms):
    x, y = restroom.exterior.xy
    plt.fill(x, y, color="blue", alpha=0.6)  # Blue polygons for restrooms
    plt.text(restroom.centroid.x, restroom.centroid.y, f"R{i+1}", fontsize=8, ha='center')

# Plot each building footprint
for building in buildings:
    x, y = building.exterior.xy
    plt.fill(x, y, color="gray", alpha=0.5)  # Gray color for buildings

# Plot edges in the Minimum Spanning Tree (MST)
for u, v, data in mst.edges(data=True):
    poly1, poly2 = restrooms[u], restrooms[v]
    centroid1, centroid2 = poly1.centroid, poly2.centroid
    plt.plot([centroid1.x, centroid2.x], [centroid1.y, centroid2.y], 'g-', linewidth=2)  # Green lines for MST edges

plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")
plt.title("Restroom Connections (Avoiding Building Footprints)")
plt.grid(True)
plt.show()
