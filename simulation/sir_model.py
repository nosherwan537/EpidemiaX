import random

def initialize_infection(G, percent_infected=0.01):
    num_initially_infected = int(len(G.nodes) * percent_infected)
    initial_infected_nodes = random.sample(list(G.nodes), num_initially_infected)
    status ={node: "S" for node in G.nodes}  # S for Susceptible
    for node in initial_infected_nodes:
        status[node] = "I"  # I for Infected

    infection_day= {node: 0 for node in G.nodes}  # Track the day of infection
    return status, infection_day, initial_infected_nodes

def simulate_sir(G, status, infection_day, max_days=100, infection_prob=0.05, recovery_time=14):
    timeline = []
    current_day = 0
    active_infected = set(infection_day.keys())

    while current_day < max_days and active_infected:
        new_infected = set()
        new_recovered = set()

        for node in list(active_infected):
            for neighbor in G.neighbors(node):
                if status[neighbor] == "S" and random.random() < infection_prob:
                    new_infected.add(neighbor)
                    status[neighbor] = "I"
                    infection_day[neighbor] = current_day

            if current_day - infection_day[node] >= recovery_time:
                new_recovered.add(node)
                status[node] = "R"

        active_infected.update(new_infected)
        active_infected.difference_update(new_recovered)

        counts={
            "day"  : current_day,
            "S"    : sum(1 for s in status.values() if s == "S"),
            "I"    : sum(1 for s in status.values() if s == "I"),
            "R"    : sum(1 for s in status.values() if s == "R"),
        }
        timeline.append(counts)
        current_day += 1

    return timeline
