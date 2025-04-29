import networkx as nx
import matplotlib.pyplot as plt
import random
import os

NUM_NODES=3000
EDGES_PER_NODE=5

def generate_social_network(num_nodes=NUM_NODES, edges_per_node=EDGES_PER_NODE):
    """
    Generate a random social network using the Barabási-Albert model.
    
    Parameters:
    num_nodes (int): Number of nodes in the network.
    edges_per_node (int): Number of edges to attach from a new node to existing nodes.
    
    Returns:
    G (networkx.Graph): Generated social network graph.
    """
    print(f"Generating a social network with {num_nodes} nodes and {edges_per_node} edges per node...")
    # Create a Barabási-Albert graph
    G = nx.barabasi_albert_graph(num_nodes, edges_per_node)
    
    return G

def save_network(G, path="network/social_network.gml"):
    """
    Save the generated network to a file.
    
    Parameters:
    G (networkx.Graph): The graph to save.
    path (str): The file path to save the graph.
    """
    print(f"Saving the network to {path}...")
    # Ensure the directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Save the graph in GML format
    nx.write_gml(G, path)
    print(f"Network saved successfully to {path}.")

if __name__ == "__main__":
    # Generate the social network
    G= generate_social_network()
    save_network(G)

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(8, 8))
    nx.draw(G, pos, node_size=10, node_color='gray')
    plt.title("Generated Social Network (Barabási-Albert Model)")
    plt.show()