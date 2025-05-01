import matplotlib.pyplot as plt
import networkx as nx
import random
import matplotlib.animation as animation
import os
import streamlit as st

def visualize_social_network_dynamic(G, status, pos=None, interval=300, seed=42):
    """
    Visualizes the social network dynamically with the status of nodes updated over time.
    
    Parameters:
    - G (networkx.Graph): The social network graph.
    - status (dict): A dictionary mapping nodes to their status ('S' for Susceptible, 'I' for Infected, 'R' for Recovered).
    - pos (dict, optional): The positions of nodes for visualization. If None, a layout will be generated.
    - interval (int): Delay between frames in milliseconds.
    - seed (int): Seed for consistent layout generation.
    """
    if pos is None:
        pos = nx.spring_layout(G, seed=seed)

    # Define colors for Susceptible, Infected, and Recovered nodes
    def get_color_map(status_dict):
        return [
            "green" if status_dict[n] == "S" else
            "red" if status_dict[n] == "I" else
            "blue"
            for n in G.nodes
        ]

    # Initialize the plot
    fig, ax = plt.subplots(figsize=(10, 10))

    def update(frame):
        ax.clear()  # Clear the axes for the new frame
        
        # Get color map for the current frame's node statuses
        color_map = get_color_map(status[frame])

        # Draw the nodes and edges
        nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=30, ax=ax, alpha=0.8)
        nx.draw_networkx_edges(G, pos, edge_color="#CCCCCC", width=0.5, alpha=0.4, ax=ax)
        
        # Set plot title and appearance
        ax.set_title(f"Day {frame} — Infection Spread", fontsize=14)
        ax.axis('off')  # Hide the axis

    # Create a dynamic animation with `FuncAnimation`
    ani = animation.FuncAnimation(
        fig, update, frames=len(status), interval=interval, repeat=False
    )
    plt.show()

def plot_sir_timeline(timeline):
    """
    Plots the timeline of S, I, R over simulation days.
    """

    days = [entry["day"] for entry in timeline]
    S = [entry["S"] for entry in timeline]
    I = [entry["I"] for entry in timeline]
    R = [entry["R"] for entry in timeline]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(days, S, label="Susceptible", color="green")
    ax.plot(days, I, label="Infected", color="red")
    ax.plot(days, R, label="Recovered", color="blue")
    ax.set_xlabel("Day")
    ax.set_ylabel("Number of Individuals")
    ax.set_title("SIR Model Simulation Over Time")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)  # This replaces plt.show()

def animate_infection_spread(G, status_history, path="visualization/infection_animation.gif", interval=300, seed=42):
    """
    Create and save an animation of infection spread and display it in Streamlit.

    Parameters:
    - G (networkx.Graph): Social network graph.
    - status_history (list of dict): List of node status dicts per day.
    - path (str): Output file path for the animation.
    - interval (int): Delay between frames in ms.
    - seed (int): Layout seed.
    """
    pos = nx.spring_layout(G, seed=seed)
    fig, ax = plt.subplots(figsize=(8, 8))

    def get_color_map(status_dict):
        return [
            "green" if status_dict[n] == "S" else
            "red" if status_dict[n] == "I" else
            "blue"
            for n in G.nodes
        ]

    def update(frame):
        ax.clear()
        color_map = get_color_map(status_history[frame])
        nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=10, ax=ax, alpha=0.8)
        nx.draw_networkx_edges(G, pos, edge_color="#CCCCCC", width=0.5, alpha=0.4, ax=ax)
        ax.set_title(f"Day {frame}", fontsize=14)
        ax.axis("off")

    ani = animation.FuncAnimation(fig, update, frames=len(status_history), interval=interval)

    # Save animation as GIF
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ani.save(path, writer="pillow", dpi=100)

    # Display in Streamlit
    st.image(path, caption="Infection Spread Animation", use_column_width=True)