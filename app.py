import streamlit as st
import networkx as nx
from network.generate_network import generate_social_network
from simulation.sihrd_model import initialize_population, simulate_sihrd, Status
from visualization.enhanced_plot import (
    plot_sihrd_timeline,
    create_age_distribution_plot,
    animate_spread,
    create_static_network,
    animate_sihrd_timeline
)
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter
import tempfile
import os

# Page configuration
st.set_page_config(
    page_title="EpidemiaX - Advanced Disease Spread Simulator",
    page_icon="🦠",
    layout="wide"
)

# Theme toggle - Day/Night
theme = st.sidebar.selectbox("Select Theme", ["Day", "Night"])

# CSS for Day and Night themes
if theme == "Day":
    st.markdown("""
        <style>
            /* Main container styling */
            .stApp {
                background: #ffffff;
            }
            
            /* Title and headers */
            .custom-title {
                font-size: 2.5rem;
                font-weight: 700;
                color: #1f77b4;
                margin-bottom: 1.5rem;
                text-align: center;
                font-family: 'Helvetica Neue', sans-serif;
            }
            
            /* Subheaders */
            .custom-subheader {
                color: #2c3e50;
                font-size: 1.5rem;
                font-weight: 600;
                margin: 1.5rem 0 1rem 0;
                padding-bottom: 0.5rem;
                border-bottom: 2px solid #eee;
            }
            
            /* Metrics styling */
            .stMetric {
                background: #f8f9fa;
                padding: 1rem;
                border-radius: 6px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            /* Tab styling */
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px;
                background-color: #f8f9fa;
                padding: 0.5rem;
                border-radius: 6px;
            }
            
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                padding: 0 16px;
                background-color: white;
                border-radius: 6px;
                color: #2c3e50;
                font-weight: 500;
                border: 1px solid #eee;
            }
            
            .stTabs [aria-selected="true"] {
                background-color: #1f77b4 !important;
                color: white !important;
            }
            
            /* Plot container styling */
            [data-testid="stPlotlyChart"], [data-testid="stImage"] {
                background: white;
                padding: 1rem;
                border-radius: 6px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                margin: 1rem 0;
            }
            
            /* Info boxes */
            .stInfo {
                background-color: #f8f9fa;
                padding: 1rem;
                border-radius: 6px;
                border-left: 4px solid #1f77b4;
            }
            
            /* Success message styling */
            .stSuccess {
                background-color: #d4edda;
                border-left: 4px solid #28a745;
            }
            
            /* Footer styling */
            footer {
                margin-top: 3rem;
                padding: 1.5rem 0;
                text-align: center;
                font-size: 0.9rem;
                color: #666;
                border-top: 1px solid #eee;
            }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            /* Main container styling */
            .stApp {
                background: #1a1a1a;
            }
            
            /* Title and headers */
            .custom-title {
                font-size: 2.5rem;
                font-weight: 700;
                color: #3498db;
                margin-bottom: 1.5rem;
                text-align: center;
                font-family: 'Helvetica Neue', sans-serif;
            }
            
            /* Subheaders */
            .custom-subheader {
                color: #e0e0e0;
                font-size: 1.5rem;
                font-weight: 600;
                margin: 1.5rem 0 1rem 0;
                padding-bottom: 0.5rem;
                border-bottom: 2px solid #333;
            }
            
            /* Metrics styling */
            .stMetric {
                background: #2d2d2d;
                padding: 1rem;
                border-radius: 6px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.2);
                color: #e0e0e0;
            }
            
            /* Tab styling */
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px;
                background-color: #2d2d2d;
                padding: 0.5rem;
                border-radius: 6px;
            }
            
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                padding: 0 16px;
                background-color: #333;
                border-radius: 6px;
                color: #e0e0e0;
                font-weight: 500;
                border: 1px solid #444;
            }
            
            .stTabs [aria-selected="true"] {
                background-color: #3498db !important;
                color: white !important;
            }
            
            /* Plot container styling */
            [data-testid="stPlotlyChart"], [data-testid="stImage"] {
                background: #2d2d2d;
                padding: 1rem;
                border-radius: 6px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.2);
                margin: 1rem 0;
            }
            
            /* Info boxes */
            .stInfo {
                background-color: #2d2d2d;
                padding: 1rem;
                border-radius: 6px;
                border-left: 4px solid #3498db;
                color: #e0e0e0;
            }
            
            /* Success message styling */
            .stSuccess {
                background-color: #2d3748;
                border-left: 4px solid #28a745;
                color: #e0e0e0;
            }
            
            /* Footer styling */
            footer {
                margin-top: 3rem;
                padding: 1.5rem 0;
                text-align: center;
                font-size: 0.9rem;
                color: #888;
                border-top: 1px solid #333;
            }
            
            /* Text color for dark theme */
            .stMarkdown, .stText {
                color: #e0e0e0;
            }
        </style>
    """, unsafe_allow_html=True)

# Header
st.markdown('<h1 class="custom-title">🦠 EpidemiaX - Disease Spread Simulator</h1>', unsafe_allow_html=True)

# Introduction with better formatting
st.markdown("""
<div style='padding: 1.5rem; background: {}; border-radius: 6px; margin-bottom: 2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
    <h3 style='color: {}; margin-bottom: 1rem;'>About the Simulator</h3>
    <p style='font-size: 1.1rem; line-height: 1.6; color: {};'>
        This application simulates the spread of an infectious disease through a population, considering multiple factors:
    </p>
    <ul style='list-style-type: none; padding-left: 0; margin-top: 1rem;'>
        <li style='margin: 0.5rem 0; color: {}; display: flex; align-items: center;'>
            <span style='margin-right: 10px;'>🎯</span> Age-based risk factors
        </li>
        <li style='margin: 0.5rem 0; color: {}; display: flex; align-items: center;'>
            <span style='margin-right: 10px;'>💉</span> Vaccination status
        </li>
        <li style='margin: 0.5rem 0; color: {}; display: flex; align-items: center;'>
            <span style='margin-right: 10px;'>🤝</span> Proximity-based transmission
        </li>
        <li style='margin: 0.5rem 0; color: {}; display: flex; align-items: center;'>
            <span style='margin-right: 10px;'>🏥</span> Hospitalization capacity
        </li>
        <li style='margin: 0.5rem 0; color: {}; display: flex; align-items: center;'>
            <span style='margin-right: 10px;'>📊</span> Mortality rates
        </li>
    </ul>
</div>
""".format(
    '#f8f9fa' if theme == "Day" else '#2d2d2d',
    '#2c3e50' if theme == "Day" else '#e0e0e0',
    '#2c3e50' if theme == "Day" else '#e0e0e0',
    '#2c3e50' if theme == "Day" else '#e0e0e0',
    '#2c3e50' if theme == "Day" else '#e0e0e0',
    '#2c3e50' if theme == "Day" else '#e0e0e0',
    '#2c3e50' if theme == "Day" else '#e0e0e0',
    '#2c3e50' if theme == "Day" else '#e0e0e0'
), unsafe_allow_html=True)

# Sidebar for parameters
st.sidebar.header("Simulation Parameters")

# Network parameters
st.sidebar.subheader("Network Parameters")
population_size = st.sidebar.slider("Population Size", 100, 1000, 500)
avg_connections = st.sidebar.slider("Average Connections per Person", 2, 20, 10)

# Disease parameters
st.sidebar.subheader("Disease Parameters")
initial_infected = st.sidebar.slider("Initial Infected (%)", 0.1, 10.0, 1.0)
infection_prob = st.sidebar.slider("Base Infection Probability", 0.01, 0.20, 0.05)
recovery_time = st.sidebar.slider("Average Recovery Time (days)", 7, 30, 14)
hospital_recovery_time = st.sidebar.slider("Hospital Recovery Time (days)", 10, 40, 21)

# Healthcare system parameters
st.sidebar.subheader("Healthcare System Parameters")
hospitalization_prob = st.sidebar.slider("Base Hospitalization Probability", 0.05, 0.30, 0.15)
death_prob = st.sidebar.slider("Base Death Probability", 0.01, 0.10, 0.02)

# Run simulation button
if st.sidebar.button("Run Simulation"):
    # Generate network
    with st.spinner("Generating social network..."):
        G = generate_social_network(num_nodes=population_size, edges_per_node=avg_connections)
        
    # Initialize population
    with st.spinner("Initializing population..."):
        status, infection_day, hospitalization_day, infected_nodes = initialize_population(
            G, percent_infected=initial_infected/100
        )
        
    # Run simulation
    with st.spinner("Running simulation..."):
        params = {
            'max_days': 100,
            'infection_prob': infection_prob,
            'hospitalization_prob': hospitalization_prob,
            'death_prob': death_prob,
            'recovery_time': recovery_time,
            'hospital_recovery_time': hospital_recovery_time
        }
        
        timeline, status_history = simulate_sihrd(
            G, status, infection_day, hospitalization_day, params
        )
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Disease Spread", "Demographics", "Network View"])
    
    # Display all static content first
    with tab1:
        st.markdown('<h2 class="custom-subheader">Disease Spread Over Time</h2>', unsafe_allow_html=True)
        
        # Static timeline with enhanced container
        st.markdown('<div class="custom-subheader">Static Timeline</div>', unsafe_allow_html=True)
        fig = plot_sihrd_timeline(timeline)
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate key metrics
        final_stats = {
            'Total Infected': timeline['infected'][-1] + timeline['hospitalized'][-1] + timeline['recovered'][-1] + timeline['deceased'][-1],
            'Peak Hospitalized': max(timeline['hospitalized']),
            'Total Deceased': timeline['deceased'][-1],
            'Recovery Rate': (timeline['recovered'][-1] / 
                            (timeline['recovered'][-1] + timeline['deceased'][-1]) * 100 if (timeline['recovered'][-1] + timeline['deceased'][-1]) > 0 else 0)
        }
        
        # Key metrics with enhanced styling
        st.markdown('<div class="custom-subheader">Key Metrics</div>', unsafe_allow_html=True)
        metrics_container = st.container()
        with metrics_container:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Infected", f"{final_stats['Total Infected']:,}")
            with col2:
                st.metric("Peak Hospitalized", f"{final_stats['Peak Hospitalized']:,}")
            with col3:
                st.metric("Total Deceased", f"{final_stats['Total Deceased']:,}")
            with col4:
                st.metric("Recovery Rate", f"{final_stats['Recovery Rate']:.1f}%")

    with tab2:
        st.subheader("Demographic Analysis")
        demo_fig = create_age_distribution_plot(G, status)
        st.plotly_chart(demo_fig, use_container_width=True)
    
    with tab3:
        st.subheader("Network Visualization")
        
        # Static network structure
        st.markdown("### Network Structure")
        static_fig = create_static_network(G)
        st.pyplot(static_fig)

    # Now handle dynamic content generation
    with tab1:
        st.markdown("### Dynamic Timeline")
        timeline_progress = st.progress(0)
        st.markdown("Generating timeline animation...")
        
        # Generate timeline animation
        anim = animate_sihrd_timeline(timeline)
        
        # Save animation to temporary file
        with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as temp_file:
            writer = PillowWriter(fps=10, bitrate=1500)
            anim.save(
                temp_file.name,
                writer=writer,
                dpi=80,
                savefig_kwargs={
                    'facecolor': 'white',
                    'bbox_inches': None,
                    'pad_inches': 0
                }
            )
            
            timeline_progress.progress(100)
            st.success("Timeline animation generated successfully!")
            
            # Create columns for centered display
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(temp_file.name, use_container_width=True)
        
        plt.close('all')
        os.unlink(temp_file.name)

    with tab3:
        st.markdown("### Disease Spread Animation")
        network_progress = st.progress(0)
        st.markdown("Generating network animation...")
        
        # Generate network animation
        anim = animate_spread(G, status_history)
        
        # Save animation to temporary file
        with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as temp_file:
            writer = PillowWriter(
                fps=5,
                bitrate=1500
            )
            
            anim.save(
                temp_file.name,
                writer=writer,
                dpi=80,
                savefig_kwargs={
                    'facecolor': 'white',
                    'bbox_inches': None,
                    'pad_inches': 0
                }
            )
            
            network_progress.progress(100)
            st.success("Network animation generated successfully!")
            
            # Create columns for centered display
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(temp_file.name, use_container_width=True)
        
        plt.close('all')
        os.unlink(temp_file.name)

else:
    st.info("Adjust the parameters in the sidebar and click 'Run Simulation' to start.")

# Enhanced footer
st.markdown("""
<footer>
    <div style='display: flex; justify-content: center; align-items: center; gap: 2rem;'>
        <span>© 2025 EpidemiaX Team</span>
        <span>|</span>
        <span>Disease Spread Simulator</span>
    </div>
</footer>
""", unsafe_allow_html=True)
