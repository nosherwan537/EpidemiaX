import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import numpy as np
from simulation.sihrd_model import Status
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def animate_sihrd_timeline(timeline):
    """Create an animated visualization of the SIHRD timeline."""
    # Create figure with subplots
    fig = plt.figure(figsize=(10, 6), dpi=80)
    ax = plt.gca()
    
    # Define colors for each status
    colors = {
        'susceptible': '#0000ff',  # Blue
        'infected': '#ff0000',     # Red
        'hospitalized': '#ffaa00', # Orange
        'recovered': '#44ff44',    # Green
        'deceased': '#000000'      # Black
    }
    
    # Get max value for y-axis scaling
    max_value = max(max(timeline[status]) for status in colors.keys())
    
    # Create x-axis data
    days = list(range(len(timeline['susceptible'])))
    
    def update(frame):
        plt.clf()
        ax = plt.gca()
        
        # Plot each status up to the current frame
        for status, color in colors.items():
            plt.plot(
                days[:frame+1],
                timeline[status][:frame+1],
                color=color,
                label=status.capitalize(),
                linewidth=2
            )
        
        # Set consistent axis limits
        plt.xlim(0, len(days))
        plt.ylim(0, max_value * 1.1)
        
        # Add labels and title
        plt.xlabel('Days', fontsize=10)
        plt.ylabel('Number of Individuals', fontsize=10)
        plt.title(f'Population Status Over Time - Day {frame}', pad=10, fontsize=12)
        
        # Add legend
        plt.legend(
            loc='center left',
            bbox_to_anchor=(1, 0.5),
            fontsize=10
        )
        
        # Grid and styling
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
    
    # Create animation
    anim = animation.FuncAnimation(
        fig,
        update,
        frames=len(days),
        interval=100,
        repeat=True
    )
    
    return anim

def plot_sihrd_timeline(timeline):
    """Create an interactive plotly visualization of the SIHRD timeline."""
    fig = go.Figure()
    
    # Add traces for each status
    colors = {
        'susceptible': '#0000ff',  # Blue
        'infected': '#ff0000',     # Red
        'hospitalized': '#ffaa00', # Orange
        'recovered': '#44ff44',    # Green
        'deceased': '#000000'      # Black
    }
    
    for status, color in colors.items():
        fig.add_trace(go.Scatter(
            x=list(range(len(timeline[status]))),
            y=timeline[status],
            name=status.capitalize(),
            line=dict(color=color, width=2),
            hovertemplate="Day %{x}<br>" +
                         f"{status.capitalize()}: %{{y}}<extra></extra>"
        ))
    
    fig.update_layout(
        title="Population Status Over Time",
        xaxis_title="Days",
        yaxis_title="Number of Individuals",
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.05
        ),
        showlegend=True,
        template="plotly_white",
        height=400  # Reduced height for better layout
    )
    
    return fig

def create_age_distribution_plot(G, status):
    """Create age distribution plots for different status groups."""
    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=("Age Distribution by Status",
                                      "Risk Factor Distribution",
                                      "Vaccination Status Impact",
                                      "Infection Rate by Age Group"))
    
    # Age distribution by status
    age_data = {s: [] for s in Status}
    for node, node_status in status.items():
        age_data[node_status].append(G.nodes[node]['age'])
    
    for s, ages in age_data.items():
        if ages:  # Only plot if we have data
            fig.add_trace(
                go.Histogram(x=ages, name=s.name, opacity=0.7),
                row=1, col=1
            )
    
    # Risk factor distribution
    risk_factors = [G.nodes[node]['risk_factor'] for node in G.nodes()]
    fig.add_trace(
        go.Histogram(x=risk_factors, name="Risk Factors"),
        row=1, col=2
    )
    
    # Vaccination impact
    vacc_status = {True: {'infected': 0, 'total': 0},
                   False: {'infected': 0, 'total': 0}}
    
    for node in G.nodes():
        is_vacc = G.nodes[node]['vaccinated']
        vacc_status[is_vacc]['total'] += 1
        if status[node] in [Status.INFECTED, Status.HOSPITALIZED]:
            vacc_status[is_vacc]['infected'] += 1
    
    vacc_rates = [
        vacc_status[True]['infected'] / vacc_status[True]['total'],
        vacc_status[False]['infected'] / vacc_status[False]['total']
    ]
    
    fig.add_trace(
        go.Bar(x=['Vaccinated', 'Unvaccinated'],
               y=vacc_rates,
               name="Infection Rate"),
        row=2, col=1
    )
    
    # Age group infection rates
    age_groups = [(0, 20), (21, 40), (41, 60), (61, 80), (81, 100)]
    age_infection_rates = []
    age_group_labels = []
    
    for start, end in age_groups:
        group_nodes = [n for n in G.nodes() 
                      if start <= G.nodes[n]['age'] <= end]
        infected = sum(1 for n in group_nodes 
                      if status[n] in [Status.INFECTED, Status.HOSPITALIZED])
        rate = infected / len(group_nodes) if group_nodes else 0
        age_infection_rates.append(rate)
        age_group_labels.append(f"{start}-{end}")
    
    fig.add_trace(
        go.Bar(x=age_group_labels,
               y=age_infection_rates,
               name="Age Group Infection Rate"),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False)
    return fig

def create_static_network(G):
    """Create a static visualization of the network structure."""
    # Reduced figure size
    fig = plt.figure(figsize=(8, 6), dpi=80)
    
    # Use the same layout parameters as animation for consistency
    pos = nx.spring_layout(
        G,
        k=1.2,
        iterations=100,
        seed=42,
        scale=2.5  # Reduced scale
    )
    
    # Draw edges first
    nx.draw_networkx_edges(
        G, pos,
        alpha=0.2,
        width=0.2,
        edge_color='gray'
    )
    
    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos,
        node_color='lightblue',
        node_size=30,  # Slightly smaller nodes
        alpha=1.0,
        edgecolors='white',
        linewidths=0.3
    )
    
    plt.title("Network Structure", pad=20, fontsize=12)
    plt.axis('off')
    return fig

def animate_spread(G, status_history):
    """Create an animated visualization of the disease spread."""
    # Reduced figure size
    fig = plt.figure(figsize=(10, 8), dpi=80)
    
    # Improved spring layout parameters
    pos = nx.spring_layout(
        G,
        k=1.2,
        iterations=100,
        seed=42,
        scale=2.5  # Reduced scale
    )
    
    # Updated color scheme
    colors = {
        Status.SUSCEPTIBLE: '#0000ff',  # Blue
        Status.INFECTED: '#ff0000',     # Red
        Status.HOSPITALIZED: '#ffaa00',  # Orange
        Status.RECOVERED: '#44ff44',    # Green
        Status.DECEASED: '#000000'      # Black
    }
    
    # Pre-calculate frame data
    frame_data = []
    
    # Pre-calculate node positions and colors for each frame
    for frame, current_status in enumerate(status_history):
        frame_nodes = {s: [] for s in Status}
        for node, node_status in current_status.items():
            frame_nodes[node_status].append(node)
        frame_data.append(frame_nodes)
    
    # Set fixed bounds for consistent view
    margin = 0.3  # Reduced margin
    x_values = [x for x, _ in pos.values()]
    y_values = [y for _, y in pos.values()]
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values), max(y_values)
    plt.xlim(x_min - margin, x_max + margin)
    plt.ylim(y_min - margin, y_max + margin)
    
    def update(frame):
        plt.clf()
        ax = plt.gca()
        
        # Set consistent bounds
        ax.set_xlim(x_min - margin, x_max + margin)
        ax.set_ylim(y_min - margin, y_max + margin)
        
        # Draw edges
        nx.draw_networkx_edges(
            G, pos,
            alpha=0.2,
            width=0.2,
            edge_color='gray'
        )
        
        # Draw nodes for each status
        for s in Status:
            nodes = frame_data[frame][s]
            if nodes:
                nx.draw_networkx_nodes(
                    G, pos,
                    nodelist=nodes,
                    node_color=colors[s],
                    node_size=30,  # Smaller nodes
                    alpha=1.0,
                    label=s.name,
                    edgecolors='white',
                    linewidths=0.3
                )
        
        plt.title(f"Disease Spread - Day {frame}", pad=15, fontsize=12)
        legend = plt.legend(
            bbox_to_anchor=(1.02, 1),
            loc='upper left',
            borderaxespad=0,
            frameon=True,
            fancybox=True,
            shadow=True,
            fontsize=10  # Smaller font
        )
        
        # Ensure proper spacing
        plt.tight_layout()
        plt.subplots_adjust(right=0.85)
        ax.axis('off')
    
    # Animation settings optimized for GIF
    anim = animation.FuncAnimation(
        fig,
        update,
        frames=len(status_history),
        interval=200,  # Slightly slower for better GIF viewing
        repeat=True
    )
    return anim 