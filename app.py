import streamlit as st
from network.generate_network import generate_social_network
from simulation.sir_model import initialize_infection, simulate_sir
from visualization.plot import plot_sir_timeline, animate_infection_spread

# Custom CSS for UI Styling
st.markdown("""
    <style>
        /* Global styling */
        body {
            background-color: #f0f4f8;
            font-family: 'Arial', sans-serif;
        }

        /* Title */
        .stApp {
            background-color: #ffffff;
        }
        .css-1d391kg {
            font-size: 3rem;
            font-weight: bold;
            color: #4b0082;
        }

        /* Sidebar */
        .css-1y4p8gk {
            background-color: #4b0082;
            color: white;
            border-radius: 10px;
        }
        .css-2y2wsu {
            background-color: #4b0082;
            color: white;
        }

        /* Button styles */
        .css-18e3p2g {
            background-color: #4b0082;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 10px 30px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        .css-18e3p2g:hover {
            background-color: #6a0dad;
        }

        /* Slider styling */
        .stSlider > div {
            margin-top: 5px;
        }

        /* Subheader styling */
        .css-1v0mbdj {
            font-size: 1.5rem;
            color: #4b0082;
            font-weight: bold;
            padding-bottom: 10px;
        }

        /* Success message */
        .css-ffhzg2 {
            background-color: #28a745;
            color: white;
            font-size: 1.2rem;
            font-weight: bold;
        }

        /* Adjust the plot title */
        .css-1mcjz01 {
            font-size: 1.5rem;
            color: #4b0082;
        }

        /* Plot styling */
        .css-1l6jwp0 {
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
    </style>
""", unsafe_allow_html=True)

# Title of the app
st.title("📊 EpidemiaX - SIR Model Simulator")

# Sidebar controls
st.sidebar.markdown("## 🧪 EpidemiaX Controls")
num_nodes = st.sidebar.slider("Number of Nodes", 100, 3000, 500, step=100)
edges_per_node = st.sidebar.slider("Edges per Node", 1, 10, 3)
infection_prob = st.sidebar.slider("Infection Probability", 0.01, 0.5, 0.05)
recovery_time = st.sidebar.slider("Recovery Time (days)", 1, 30, 14)
max_days = st.sidebar.slider("Max Simulation Days", 10, 200, 100)
percent_infected = st.sidebar.slider("Initial % Infected", 0.01, 0.1, 0.01)

if st.button("Run Simulation"):
    # Generate the social network
    G = generate_social_network(num_nodes, edges_per_node)
    
    # Initialize infection
    status, infection_day, _ = initialize_infection(G, percent_infected)
    
    # Simulate the infection spread
    timeline, status_history = simulate_sir(G, status, infection_day, max_days, infection_prob, recovery_time)

    # SIR Timeline plot
    st.subheader("📈 SIR Timeline")
    plot_sir_timeline(timeline)

    # Infection Spread Animation
    st.subheader("🎞️ Infection Spread Animation")
    animate_infection_spread(G, status_history)

    # Display success message
    st.success("✅ Simulation complete!")
    st.balloons()