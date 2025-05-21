import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import numpy as np
from simulation.sihrd_model import Status
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Any

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
    
    # Create x-axis data - reduce frames by taking every 2nd day
    days = list(range(0, len(timeline['susceptible']), 2))
    lines = {}
    
    # Initialize empty lines
    for status in colors.keys():
        line, = plt.plot([], [], color=colors[status], label=status.capitalize(), linewidth=2)
        lines[status] = line
    
    # Set consistent axis limits
    plt.xlim(0, len(timeline['susceptible']))
    plt.ylim(0, max_value * 1.1)
    
    # Add labels and title
    plt.xlabel('Days', fontsize=10)
    plt.ylabel('Number of Individuals', fontsize=10)
    plt.title('Population Status Over Time', pad=10, fontsize=12)
    
    # Add legend
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
    
    # Grid and styling
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    def update(frame):
        real_frame = frame * 2  # Account for frame skipping
        # Update line data
        for status, line in lines.items():
            line.set_data(
                range(real_frame + 1),
                timeline[status][:real_frame + 1]
            )
        plt.title(f'Population Status Over Time - Day {real_frame}', pad=10, fontsize=12)
        return list(lines.values())
    
    # Create animation with optimized parameters
    anim = animation.FuncAnimation(
        fig,
        update,
        frames=len(days),
        interval=200,  # Increased interval for smoother playback
        blit=True,  # Enable blit for better performance
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
    # Validate input
    if not status_history or len(status_history) == 0:
        raise ValueError("No status history data provided for animation")

    # Further reduced figure size and DPI for better performance
    plt.ioff()  # Turn off interactive mode
    fig = plt.figure(figsize=(8, 6), dpi=60)
    
    # Calculate layout with fewer iterations for speed
    pos = nx.spring_layout(G, k=1.2, iterations=30, seed=42, scale=2.0)
    
    # Updated color scheme
    colors = {
        Status.SUSCEPTIBLE: '#0000ff',  # Blue
        Status.INFECTED: '#ff0000',     # Red
        Status.HOSPITALIZED: '#ffaa00',  # Orange
        Status.RECOVERED: '#44ff44',    # Green
        Status.DECEASED: '#000000'      # Black
    }
    
    # Pre-calculate frame data with more aggressive frame skipping
    frame_data = []
    step = 4  # Skip every 4 frames
    
    # Ensure we always have at least 10 frames for smooth animation
    if len(status_history) < 40:  # If less than 40 frames, adjust step size
        step = max(1, len(status_history) // 10)
    
    for frame_idx in range(0, len(status_history), step):
        current_status = status_history[frame_idx]
        frame_nodes = {s: [] for s in Status}
        for node, node_status in current_status.items():
            frame_nodes[node_status].append(node)
        frame_data.append(frame_nodes)
    
    # Ensure we have at least one frame
    if not frame_data:
        plt.close(fig)
        raise ValueError("No frames generated for animation")
    
    # Set fixed bounds with smaller margin
    margin = 0.2
    x_values = [x for x, _ in pos.values()]
    y_values = [y for _, y in pos.values()]
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values), max(y_values)
    
    # Create static elements
    ax = plt.gca()
    ax.set_xlim(x_min - margin, x_max + margin)
    ax.set_ylim(y_min - margin, y_max + margin)
    
    # Draw edges once with reduced alpha and width
    edge_collection = nx.draw_networkx_edges(
        G, pos,
        alpha=0.1,
        width=0.1,
        edge_color='gray'
    )
    
    # Initialize node collections with smaller nodes
    node_collections = {}
    for s in Status:
        node_collections[s] = ax.scatter([], [], c=colors[s], s=20, label=s.name)
    
    def init():
        """Initialize animation"""
        for collection in node_collections.values():
            collection.set_offsets(np.empty((0, 2)))
        return list(node_collections.values())
    
    def update(frame):
        """Update animation frame"""
        try:
            # Update node positions for each status
            for s in Status:
                nodes = frame_data[frame][s]
                if nodes:
                    node_pos = np.array([pos[node] for node in nodes])
                    node_collections[s].set_offsets(node_pos)
                else:
                    node_collections[s].set_offsets(np.empty((0, 2)))
            
            ax.set_title(f"Disease Spread - Day {frame * step}", pad=10, fontsize=10)
            return list(node_collections.values())
        except Exception as e:
            print(f"Error in update function: {str(e)}")
            return init()
    
    plt.title("Disease Spread", pad=10, fontsize=10)
    plt.legend(
        bbox_to_anchor=(1.01, 1),
        loc='upper left',
        borderaxespad=0,
        frameon=True,
        fancybox=False,
        shadow=False,
        fontsize=8
    )
    
    # Ensure proper spacing with reduced margins
    plt.tight_layout(pad=1.0)
    plt.subplots_adjust(right=0.85)
    ax.axis('off')
    
    # Create animation with optimized parameters
    anim = animation.FuncAnimation(
        fig,
        update,
        init_func=init,
        frames=len(frame_data),
        interval=100,
        blit=True,
        repeat=True
    )
    
    plt.ion()  # Turn interactive mode back on
    return anim

def create_network_plot(G: nx.Graph, pos: Dict[int, List[float]], node_colors: List[str]) -> go.Figure:
    """Create an interactive network plot using Plotly."""
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            )
        ))

    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title='Network Graph',
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20, l=5, r=5, t=40),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                   )
    return fig

def plot_sihrd_timeline(timeline: Dict[str, List[float]]) -> go.Figure:
    """Create an interactive timeline plot of SIHRD model."""
    days = range(len(timeline['susceptible']))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=days, y=timeline['susceptible'], name='Susceptible',
                            line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=days, y=timeline['infected'], name='Infected',
                            line=dict(color='red')))
    fig.add_trace(go.Scatter(x=days, y=timeline['hospitalized'], name='Hospitalized',
                            line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=days, y=timeline['recovered'], name='Recovered',
                            line=dict(color='green')))
    fig.add_trace(go.Scatter(x=days, y=timeline['deceased'], name='Deceased',
                            line=dict(color='gray')))

    fig.update_layout(
        title='Disease Spread Timeline',
        xaxis_title='Days',
        yaxis_title='Population',
        hovermode='x unified'
    )
    return fig

def create_age_distribution_plot(age_distribution: Dict[str, float]) -> go.Figure:
    """Create an interactive bar plot of age distribution."""
    fig = go.Figure(data=[
        go.Bar(
            x=list(age_distribution.keys()),
            y=list(age_distribution.values()),
            marker_color='lightblue'
        )
    ])
    
    fig.update_layout(
        title='Age Distribution',
        xaxis_title='Age Group',
        yaxis_title='Percentage',
        showlegend=False
    )
    return fig

def animate_spread(G: nx.Graph, pos: Dict[int, List[float]], 
                  timeline: Dict[str, List[float]], frames: int = 100) -> go.Figure:
    """Create an animated visualization of disease spread."""
    frames_list = []
    for i in range(frames):
        frame_data = []
        for node in G.nodes():
            status = 'susceptible'  # Default status
            if i < len(timeline['infected']) and node < len(timeline['infected']):
                if timeline['infected'][i][node] > 0:
                    status = 'infected'
                elif timeline['recovered'][i][node] > 0:
                    status = 'recovered'
                elif timeline['deceased'][i][node] > 0:
                    status = 'deceased'
            
            color = {
                'susceptible': 'blue',
                'infected': 'red',
                'recovered': 'green',
                'deceased': 'gray'
            }[status]
            
            frame_data.append(go.Scatter(
                x=[pos[node][0]],
                y=[pos[node][1]],
                mode='markers',
                marker=dict(size=10, color=color),
                name=status
            ))
        
        frames_list.append(go.Frame(data=frame_data, name=f'frame{i}'))
    
    fig = go.Figure(
        data=frames_list[0].data,
        frames=frames_list,
        layout=go.Layout(
            title='Disease Spread Animation',
            showlegend=True,
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [
                    {
                        'label': 'Play',
                        'method': 'animate',
                        'args': [None, {'frame': {'duration': 100, 'redraw': True},
                                      'fromcurrent': True}]
                    }
                ]
            }]
        )
    )
    return fig 