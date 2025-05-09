import streamlit as st
import matplotlib.pyplot as plt
import time
from network.generate_network import generate_social_network
from simulation.sir_model import initialize_infection, simulate_sir
from visualization.plot import animate_infection_spread

# Page configuration
st.set_page_config(
    page_title="EpidemiaX - SIR Model Simulator",
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
st.markdown('<h1 class="custom-title">📊 EpidemiaX - SIR Model Simulator</h1>', unsafe_allow_html=True)

# Sidebar controls
st.sidebar.markdown("## 🧪 EpidemiaX Controls")
num_nodes = st.sidebar.slider("Number of Nodes", 100, 3000, 500, step=100)
edges_per_node = st.sidebar.slider("Edges per Node", 1, 10, 3)
infection_prob = st.sidebar.slider("Infection Probability", 0.01, 0.5, 0.05)
recovery_time = st.sidebar.slider("Recovery Time (days)", 1, 30, 14)
max_days = st.sidebar.slider("Max Simulation Days", 10, 200, 100)
percent_infected = st.sidebar.slider("Initial % Infected", 0.01, 0.1, 0.01)

if st.button("Run Simulation"):
    G = generate_social_network(num_nodes, edges_per_node)
    status, infection_day, _ = initialize_infection(G, percent_infected)

    st.markdown('<div class="custom-subheader">📈 Live SIR Timeline</div>', unsafe_allow_html=True)
    center_col = st.columns([0.2, 0.6, 0.2])[1]
    plot_placeholder = center_col.empty()

    timeline_data = {"day": [], "S": [], "I": [], "R": []}
    status_history = []

    for data in simulate_sir(G, status, infection_day, max_days, infection_prob, recovery_time):
        timeline_data["day"].append(data["day"])
        timeline_data["S"].append(data["S"])
        timeline_data["I"].append(data["I"])
        timeline_data["R"].append(data["R"])
        status_history.append(data["status"])

        fig, ax = plt.subplots()
        ax.plot(timeline_data["day"], timeline_data["S"], label="Susceptible", color="blue")
        ax.plot(timeline_data["day"], timeline_data["I"], label="Infected", color="red")
        ax.plot(timeline_data["day"], timeline_data["R"], label="Recovered", color="green")
        ax.set_xlabel("Day")
        ax.set_ylabel("Count")
        ax.set_title("SIR Simulation Over Time")
        ax.legend()
        plot_placeholder.pyplot(fig, use_container_width=True)
        time.sleep(0.15)

    st.markdown('<div class="custom-subheader">🎞️ Infection Spread Animation</div>', unsafe_allow_html=True)
    center_col = st.columns([0.2, 0.6, 0.2])[1]
    with center_col:
        animate_infection_spread(G, status_history)

    st.success("✅ Simulation complete!")
    st.balloons()

# Footer
st.markdown('<footer>© 2025 EpidemiaX Team. All rights reserved.</footer>', unsafe_allow_html=True)
