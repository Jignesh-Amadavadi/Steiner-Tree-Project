import networkx as nx
from shapely.geometry import Point, Polygon, LineString
import matplotlib.pyplot as plt
import math
import random

# Define building footprints as polygons
buildings = [
    Polygon([(3, 3), (6, 3), (6, 6), (3, 6)]),  # Example building footprint
    Polygon([(8, 1), (10, 1), (10, 4), (8, 4)]) # Another building footprint
]

# Function to calculate Euclidean distance between two points
def euclidean_distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

# Function to check if a point is inside any building
def is_outside_buildings(point, buildings):
    for building in buildings:
        if building.contains(point):
            return False
    return True

# Generate random restroom points that are outside building footprints
restrooms = []
while len(restrooms) < 20:
    x, y = random.uniform(0, 12), random.uniform(0, 10)
    point = Point(x, y)
    if is_outside_buildings(point, buildings):
        restrooms.append(point)

# Function to check if a line segment intersects any building
def is_valid_path(p1, p2, buildings):
    line = LineString([p1, p2])
    for building in buildings:
        if line.intersects(building) and not line.touches(building):
            return False
    return True

# Step 1: Create a complete graph with restrooms as nodes
G = nx.Graph()
for i, p1 in enumerate(restrooms):
    for j, p2 in enumerate(restrooms):
        if i < j:
            # Only add edge if it does not intersect any building
            if is_valid_path(p1, p2, buildings):
                distance = euclidean_distance(p1, p2)
                G.add_edge(i, j, weight=distance)

# Step 2: Compute the Minimum Spanning Tree (MST) to connect all restrooms with minimal total length
mst = nx.minimum_spanning_tree(G)

# Step 3: Visualize the restrooms, buildings, and MST connections
plt.figure(figsize=(10, 10))

# Plot each restroom point
for i, restroom in enumerate(restrooms):
    plt.plot(restroom.x, restroom.y, 'bo', markersize=6)  # Blue points for restrooms
    plt.text(restroom.x + 0.1, restroom.y + 0.1, f"R{i+1}", fontsize=8)  # Label each point

# Plot each building footprint
for building in buildings:
    x, y = building.exterior.xy
    plt.fill(x, y, color="gray", alpha=0.5)  # Gray color for buildings

# Plot edges in the Minimum Spanning Tree (MST)
for u, v, data in mst.edges(data=True):
    p1, p2 = restrooms[u], restrooms[v]
    plt.plot([p1.x, p2.x], [p1.y, p2.y], 'g-', linewidth=1)  # Green lines for MST edges

# Add plot labels and titles
plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")
plt.title("Restroom Connections (Avoiding Building Footprints)")
plt.grid(True)
plt.show()
