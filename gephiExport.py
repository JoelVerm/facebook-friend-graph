import networkx as nx
import pickle

GRAPH_FILENAME = "friend_graph.pickle"

with open(GRAPH_FILENAME, "rb") as f:
    friend_graph = pickle.load(f)

# First, we'll clean the edges of the grap
edges = set()
nodes = set()

friends_connections = {}

for k, v in friend_graph.items():
    # If the friend has only one connection, we'll skip it
    if len(v) <= 1:
        continue

    nodes.add(k)
    for item in v:
        edges.add((k, item))

edges = {(u, v) for u, v in edges if u != v and u in nodes and v in nodes}

G = nx.Graph()
G.add_nodes_from(nodes)
G.add_edges_from(edges)

nx.write_gexf(G, "friends.gexf")
