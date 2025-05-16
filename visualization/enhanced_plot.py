import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import numpy as np
from simulation.sihrd_model import Status
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_network_plot(G, status, title=""):
    """Create a static network visualization with enhanced styling."""
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=1/np.sqrt(len(G.nodes())), iterations=50)
    
    # Define colors for each status
    colors = {
        Status.SUSCEPTIBLE: '#808080',  # Gray
        Status.INFECTED: '#ff4444',     # Red
        Status.HOSPITALIZED: '#ffaa00',  # Orange
        Status.RECOVERED: '#44ff44',    # Green
        Status.DECEASED: '#000000'      # Black
    }
    
    # Create node collections for each status
    for s in Status:
        nodes = [node for node, node_status in status.items() if node_status == s]
        nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color=colors[s], 
                             node_size=100, alpha=0.8, label=s.name)
    
    # Draw edges with alpha for better visibility
    nx.draw_networkx_edges(G, pos, alpha=0.1)
    
    plt.title(title, fontsize=16, pad=20)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    return plt.gcf()

def plot_sihrd_timeline(timeline):
    """Create an interactive plotly visualization of the SIHRD timeline."""
    fig = go.Figure()
    
    # Add traces for each status
    colors = {
        'susceptible': '#808080',
        'infected': '#ff4444',
        'hospitalized': '#ffaa00',
        'recovered': '#44ff44',
        'deceased': '#000000'
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
        template="plotly_white"
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

def animate_spread(G, status_history):
    """Create an animated visualization of the disease spread."""
    fig = plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=1/np.sqrt(len(G.nodes())), iterations=50)
    
    colors = {
        Status.SUSCEPTIBLE: '#808080',
        Status.INFECTED: '#ff4444',
        Status.HOSPITALIZED: '#ffaa00',
        Status.RECOVERED: '#44ff44',
        Status.DECEASED: '#000000'
    }
    
    def update(frame):
        plt.clf()
        current_status = status_history[frame]
        
        for s in Status:
            nodes = [node for node, node_status in current_status.items() 
                    if node_status == s]
            nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color=colors[s],
                                 node_size=100, alpha=0.8, label=s.name)
        
        nx.draw_networkx_edges(G, pos, alpha=0.1)
        plt.title(f"Disease Spread - Day {frame}")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
    
    anim = animation.FuncAnimation(fig, update, frames=len(status_history),
                                 interval=200, repeat=True)
    return anim 