# main.py
from network.generate_network import generate_social_network, save_network
from visualization.plot import visualize_social_network_static, plot_sir_timeline
from simulation.sir_model import initialize_infection, simulate_sir

def main():
    # Step 1: Generate social network
    G = generate_social_network()
    save_network(G)

    # Step 2: Initial static visualization
    visualize_social_network_static(G, num_infected=100)

    # Step 3: Initialize infection (1% infected)
    status, infection_day, infected_nodes = initialize_infection(G, percent_infected=0.01)

    # Step 4: Simulate infection over time (SIR model)
    timeline = simulate_sir(
        G, 
        status, 
        infection_day, 
        max_days=100, 
        infection_prob=0.05, 
        recovery_time=14
    )

    # Step 5: Plot the S, I, R trends
    plot_sir_timeline(timeline)

if __name__ == "__main__":
    main()
