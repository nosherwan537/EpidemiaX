# main.py
from network.generate_network import generate_social_network, save_network
from visualization.enhanced_plot import create_network_plot, plot_sihrd_timeline, create_age_distribution_plot, animate_spread
from simulation.sihrd_model import initialize_population, simulate_sihrd
import matplotlib.pyplot as plt

def main():
    # Step 1: Generate social network
    print("Generating social network...")
    G = generate_social_network(num_nodes=500, edges_per_node=10)
    save_network(G)

    # Step 2: Initialize population with enhanced attributes
    print("Initializing population...")
    status, infection_day, hospitalization_day, infected_nodes = initialize_population(
        G, percent_infected=0.01
    )

    # Step 3: Initial network visualization
    print("Creating initial visualization...")
    fig = create_network_plot(G, status, "Initial Network State")
    plt.show()

    # Step 4: Simulate infection spread with SIHRD model
    print("Running SIHRD simulation...")
    params = {
        'max_days': 100,
        'infection_prob': 0.05,
        'hospitalization_prob': 0.15,
        'death_prob': 0.02,
        'recovery_time': 14,
        'hospital_recovery_time': 21
    }
    
    timeline, status_history = simulate_sihrd(
        G, 
        status, 
        infection_day,
        hospitalization_day,
        params
    )

    # Step 5: Create and display visualizations
    print("Generating final visualizations...")
    
    # Plot SIHRD timeline
    timeline_fig = plot_sihrd_timeline(timeline)
    timeline_fig.show()
    
    # Create demographic analysis
    demo_fig = create_age_distribution_plot(G, status)
    demo_fig.show()
    
    # Create and save animation
    anim = animate_spread(G, status_history)
    anim.save('disease_spread.gif', writer='pillow', fps=5)
    
    print("Simulation complete! Check the output files for visualizations.")

if __name__ == "__main__":
    main()
