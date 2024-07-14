import networkx as nx
import pickle

# ! IMPORTANT !
# ! Change this constant into your facebook username !
USERNAME = "J.D. Vermeulen"
# ! IMPORTANT !

# * Filter friends that have only one connection to your friends
TOGGLE_FILTER_EDGE_FRIENDS = False
# * True results in a smaller graph

GRAPH_FILENAME = "friend_graph.pickle"

with open(GRAPH_FILENAME, "rb") as f:
    friend_graph = pickle.load(f)

# First, we'll clean the edges of the grap
edges = set()
nodes = set()

friends_connections = {}

for k, v in friend_graph.items():
    print(k)
    for item in v:
        print("- ", item)

    if TOGGLE_FILTER_EDGE_FRIENDS:
        # If the friend has only one connection, we'll skip it
        if len(v) <= 1 and not USERNAME in v:
            continue

    nodes.add(k)
    for item in v:
        edges.add((k, item))

print("\n")
print("Filtering edges...")

edges = {(u, v) for u, v in edges if u != v and u in nodes and v in nodes}

print(f"Found {len(edges)} edges between {len(nodes)} nodes")

G = nx.Graph()
G.add_nodes_from(nodes)
G.add_edges_from(edges)

if TOGGLE_FILTER_EDGE_FRIENDS:
    nx.write_gexf(G, "friends.gexf")
else:
    nx.write_gexf(G, "friends-all.gexf")

print("Done!")
