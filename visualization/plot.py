import matplotlib.pyplot as plt
import networkx as nx
import random

def visualize_social_network_static(G, num_infected=100, seed=42):
    """
    Visualize the social network using matplotlib with infected vs healthy nodes.

    Parameters:
    - G (networkx.Graph): The social network graph.
    - num_infected (int): Number of initially infected nodes.
    - seed (int): Seed for reproducible layout.
    """

    print("Generating spring layout for visualization (this may take a while)...")
    pos = nx.spring_layout(G, seed=seed)

    print(f"Selecting {num_infected} random nodes as initially infected...")
    infected_nodes = set(random.sample(list(G.nodes), num_infected))

    print("Preparing color map...")
    color_map = ['red' if node in infected_nodes else 'green' for node in G.nodes]

    print("Drawing graph...")
    plt.figure(figsize=(12, 12))
    nx.draw_networkx_nodes(G, pos, node_size=10, node_color=color_map, alpha=0.8)
    nx.draw_networkx_edges(G, pos, edge_color="#CCCCCC", width=0.5, alpha=0.5)

    plt.title("Social Network with Infected vs Healthy Nodes", fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

    print("Visualization complete.")


def plot_sir_timeline(timeline):
    """
    Plots the timeline of S, I, R over simulation days.
    """

    days = [entry["day"] for entry in timeline]
    S = [entry["S"] for entry in timeline]
    I = [entry["I"] for entry in timeline]
    R = [entry["R"] for entry in timeline]

    plt.figure(figsize=(10, 6))
    plt.plot(days, S, label="Susceptible", color="green")
    plt.plot(days, I, label="Infected", color="red")
    plt.plot(days, R, label="Recovered", color="blue")
    plt.xlabel("Day")
    plt.ylabel("Number of Individuals")
    plt.title("SIR Model Simulation Over Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
