import streamlit as st
import networkx as nx
from network.generate_network import generate_social_network
from simulation.sihrd_model import initialize_population, simulate_sihrd, Status
from visualization.enhanced_plot import (
    create_network_plot,
    plot_sihrd_timeline,
    create_age_distribution_plot,
    animate_spread
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
            html, body, .stApp {
                height: 100%;
                background: #f0f4f8;
                font-family: 'Arial', sans-serif;
                color: #333;
            }
            .stSidebar, .stSidebar * {
                background-color: #ffffff;
                color: #333;
            }
            .custom-title {
                font-size: 3rem;
                font-weight: bold;
                color: #4b0082;
                margin-bottom: 10px;
            }
            .custom-subheader {
                font-size: 1.5rem;
                color: #4b0082;
                font-weight: bold;
                margin-top: 30px;
            }
            .custom-button {
                background-color: #4b0082;
                color: white;
                font-weight: bold;
                padding: 10px 30px;
                border: none;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            .custom-button:hover {
                background-color: #6a0dad;
            }
            footer {
                margin-top: 50px;
                padding-top: 10px;
                text-align: center;
                font-size: 0.9rem;
                color: #888;
            }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            html, body, .stApp {
                height: 100%;
                background: #121212;
                font-family: 'Arial', sans-serif;
                color: #e0e0e0;
            }
            .stSidebar, .stSidebar * {
                background-color: #333333;
                color: #e0e0e0;
            }
            .custom-title {
                font-size: 3rem;
                font-weight: bold;
                color: #e0e0e0;
                margin-bottom: 10px;
            }
            .custom-subheader {
                font-size: 1.5rem;
                color: #e0e0e0;
                font-weight: bold;
                margin-top: 30px;
            }
            .custom-button {
                background-color: #6200ea;
                color: white;  /* Default text color for button */
                font-weight: bold;
                padding: 10px 30px;
                border: none;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            .custom-button:hover {
                background-color: #3700b3;
            }
            /* Apply red color to Run Simulation button in Night mode */
            .night-mode .stButton button {
                color: red;  /* Change button text color to red in Night mode */
            }
            footer {
                margin-top: 50px;
                padding-top: 10px;
                text-align: center;
                font-size: 0.9rem;
                color: #bbb;
            }
        </style>
    """, unsafe_allow_html=True)


# Header
st.markdown('<h1 class="custom-title">📊 EpidemiaX - Advanced Disease Spread Simulator</h1>', unsafe_allow_html=True)

st.title("EpidemiaX - Advanced Disease Spread Simulator")
st.markdown("""
This application simulates the spread of an infectious disease through a population,
taking into account factors such as:
- Age-based risk factors
- Vaccination status
- Proximity-based transmission
- Hospitalization capacity
- Mortality rates
""")

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
    
    # Display results in tabs
    tab1, tab2, tab3 = st.tabs(["Disease Spread", "Demographics", "Network View"])
    
    with tab1:
        st.subheader("Disease Spread Over Time")
        fig = plot_sihrd_timeline(timeline)
        st.plotly_chart(fig, use_container_width=True)
        
        # Key metrics
        final_stats = {
            'Total Infected': sum(timeline['infected']),
            'Peak Hospitalized': max(timeline['hospitalized']),
            'Total Deceased': timeline['deceased'][-1],
            'Recovery Rate': (timeline['recovered'][-1] / 
                            (timeline['recovered'][-1] + timeline['deceased'][-1]) * 100)
        }
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Infected", f"{final_stats['Total Infected']:,}")
        col2.metric("Peak Hospitalized", f"{final_stats['Peak Hospitalized']:,}")
        col3.metric("Total Deceased", f"{final_stats['Total Deceased']:,}")
        col4.metric("Recovery Rate", f"{final_stats['Recovery Rate']:.1f}%")
    
    with tab2:
        st.subheader("Demographic Analysis")
        demo_fig = create_age_distribution_plot(G, status)
        st.plotly_chart(demo_fig, use_container_width=True)
    
    with tab3:
        st.subheader("Network Visualization")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create network visualization
            network_fig = create_network_plot(G, status, "Current Network State")
            st.pyplot(network_fig)
        
        with col2:
            st.markdown("""
            ### Network Statistics
            - **Nodes:** {}
            - **Edges:** {}
            - **Average Degree:** {:.2f}
            - **Network Density:** {:.3f}
            """.format(
                G.number_of_nodes(),
                G.number_of_edges(),
                sum(dict(G.degree()).values()) / G.number_of_nodes(),
                nx.density(G)
            ))
            
            # Add animation
            st.markdown("### Animation of Disease Spread")
            anim = animate_spread(G, status_history)
            
            # Save animation to temporary file
            with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as temp_file:
                anim.save(temp_file.name, writer=PillowWriter(fps=5))
                st.image(temp_file.name)
            os.unlink(temp_file.name)  # Clean up temp file

else:
    st.info("Adjust the parameters in the sidebar and click 'Run Simulation' to start.")

# Footer
st.markdown('<footer>© 2025 EpidemiaX Team. All rights reserved.</footer>', unsafe_allow_html=True)
