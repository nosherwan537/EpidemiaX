import networkx as nx
import numpy as np
from enum import Enum
import random

class Status(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    HOSPITALIZED = 2
    RECOVERED = 3
    DECEASED = 4 

def initialize_population(G, percent_infected=0.01, preserve_attributes=False):
    """Initialize the population with various attributes."""
    status = {}
    infection_day = {}
    hospitalization_day = {}
    
    # Initialize node attributes
    for node in G.nodes():
        if not preserve_attributes:
            # Assign random age (0-100)
            G.nodes[node]['age'] = random.randint(0, 100)
            # Assign random vaccination status (0-1)
            G.nodes[node]['vaccinated'] = random.random() < 0.7  # 70% vaccination rate
            # Calculate base risk factor based on age
            age = G.nodes[node]['age']
            G.nodes[node]['risk_factor'] = calculate_risk_factor(age, G.nodes[node]['vaccinated'])
        
        status[node] = Status.SUSCEPTIBLE
        infection_day[node] = -1
        hospitalization_day[node] = -1

    # Initialize infected nodes
    infected_nodes = random.sample(list(G.nodes()), int(len(G.nodes()) * percent_infected))
    for node in infected_nodes:
        status[node] = Status.INFECTED
        infection_day[node] = 0

    return status, infection_day, hospitalization_day, infected_nodes

def calculate_risk_factor(age, vaccinated):
    """Calculate risk factor based on age and vaccination status."""
    base_risk = np.interp(age, [0, 50, 70, 85, 100], [0.1, 0.2, 0.4, 0.7, 1.0])
    return base_risk * (0.3 if vaccinated else 1.0)

def simulate_sihrd(G, status, infection_day, hospitalization_day, params):
    """
    Simulate the SIHRD model with enhanced parameters.
    """
    max_days = params.get('max_days', 100)
    base_infection_prob = params.get('infection_prob', 0.05)
    hospitalization_prob = params.get('hospitalization_prob', 0.15)
    death_prob = params.get('death_prob', 0.02)
    recovery_time = params.get('recovery_time', 14)
    hospital_recovery_time = params.get('hospital_recovery_time', 21)

    timeline = {
        'susceptible': [],
        'infected': [],
        'hospitalized': [],
        'recovered': [],
        'deceased': []
    }
    status_history = []

    current_status = status.copy()
    
    for day in range(max_days):
        # Store current state
        status_count = count_status(current_status)
        for key in timeline:
            timeline[key].append(status_count[Status[key.upper()]])
        status_history.append(current_status.copy())

        # Process infections and state changes
        new_status = current_status.copy()
        
        for node in G.nodes():
            if current_status[node] == Status.INFECTED:
                # Check for hospitalization
                if infection_day[node] >= 5:  # Consider hospitalization after 5 days
                    if (random.random() < hospitalization_prob * G.nodes[node]['risk_factor'] and 
                        hospitalization_day[node] == -1):
                        new_status[node] = Status.HOSPITALIZED
                        hospitalization_day[node] = day
                
                # Check for recovery (if not hospitalized)
                elif infection_day[node] >= recovery_time:
                    if random.random() < 0.1:  # Daily recovery chance after recovery_time
                        new_status[node] = Status.RECOVERED

            elif current_status[node] == Status.HOSPITALIZED:
                days_hospitalized = day - hospitalization_day[node]
                if days_hospitalized >= hospital_recovery_time:
                    # Either recover or die based on risk factor
                    if random.random() < death_prob * G.nodes[node]['risk_factor']:
                        new_status[node] = Status.DECEASED
                    else:
                        new_status[node] = Status.RECOVERED

            elif current_status[node] == Status.SUSCEPTIBLE:
                # Calculate infection probability based on infected neighbors
                infected_neighbors = sum(1 for neighbor in G.neighbors(node) 
                                      if current_status[neighbor] == Status.INFECTED)
                if infected_neighbors > 0:
                    # Increased probability with more infected neighbors
                    infection_prob = 1 - (1 - base_infection_prob) ** infected_neighbors
                    # Modify by risk factor and vaccination
                    infection_prob *= G.nodes[node]['risk_factor']
                    
                    if random.random() < infection_prob:
                        new_status[node] = Status.INFECTED
                        infection_day[node] = day

        # Update days for infected individuals
        for node in G.nodes():
            if new_status[node] == Status.INFECTED and current_status[node] == Status.INFECTED:
                infection_day[node] += 1

        current_status = new_status

    return timeline, status_history

def count_status(status):
    """Count the number of individuals in each state."""
    counts = {s: 0 for s in Status}
    for node_status in status.values():
        counts[node_status] += 1
    return counts 