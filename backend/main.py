from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from typing import Dict, List, Optional
import json
import random
import numpy as np
import networkx as nx

# Add parent directory to path to import simulation modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.sihrd_model import (
    initialize_population, 
    simulate_sihrd, 
    Status,
    calculate_risk_factor
)
from network.generate_network import generate_social_network

app = FastAPI(title="EpidemiaX API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def validate_parameters(params: Dict) -> None:
    """Validate all simulation parameters."""
    if not (100 <= params['num_nodes'] <= 10000):
        raise HTTPException(status_code=400, detail="Number of nodes must be between 100 and 10000")
    if not (1 <= params['edges_per_node'] <= 20):
        raise HTTPException(status_code=400, detail="Edges per node must be between 1 and 20")
    if not (0 <= params['initial_infected_percentage'] <= 1):
        raise HTTPException(status_code=400, detail="Initial infected percentage must be between 0 and 1")
    if not (10 <= params['simulation_days'] <= 365):
        raise HTTPException(status_code=400, detail="Simulation days must be between 10 and 365")
    if not (0 <= params['vaccination_rate'] <= 1):
        raise HTTPException(status_code=400, detail="Vaccination rate must be between 0 and 1")
    if not (0 <= params['mask_usage'] <= 1):
        raise HTTPException(status_code=400, detail="Mask usage must be between 0 and 1")
    if not (0 <= params['transmission_rate'] <= 1):
        raise HTTPException(status_code=400, detail="Transmission rate must be between 0 and 1")
    if not (0 <= params['recovery_rate'] <= 1):
        raise HTTPException(status_code=400, detail="Recovery rate must be between 0 and 1")
    if not (0 <= params['mortality_rate'] <= 1):
        raise HTTPException(status_code=400, detail="Mortality rate must be between 0 and 1")
    if not (0 <= params['hospitalization_rate'] <= 1):
        raise HTTPException(status_code=400, detail="Hospitalization rate must be between 0 and 1")

@app.get("/")
async def root():
    return {"message": "Welcome to EpidemiaX API"}

@app.post("/simulate")
async def run_simulation(
    num_nodes: int,
    edges_per_node: int,
    initial_infected_percentage: float,
    simulation_days: int,
    vaccination_rate: float = 0.0,
    mask_usage: float = 0.0,
    transmission_rate: float = 0.3,
    recovery_rate: float = 0.1,
    mortality_rate: float = 0.02,
    hospitalization_rate: float = 0.15
):
    try:
        # Validate parameters
        params = {
            'num_nodes': num_nodes,
            'edges_per_node': edges_per_node,
            'initial_infected_percentage': initial_infected_percentage,
            'simulation_days': simulation_days,
            'vaccination_rate': vaccination_rate,
            'mask_usage': mask_usage,
            'transmission_rate': transmission_rate,
            'recovery_rate': recovery_rate,
            'mortality_rate': mortality_rate,
            'hospitalization_rate': hospitalization_rate
        }
        validate_parameters(params)

        # Generate network
        G = generate_social_network(num_nodes, edges_per_node)
        
        # Initialize population with custom vaccination rate
        def custom_vaccination(node):
            return random.random() < vaccination_rate

        # Initialize population
        status, infection_day, hospitalization_day, infected_nodes = initialize_population(
            G,
            percent_infected=initial_infected_percentage,
            preserve_attributes=False
        )
        
        # Override vaccination status based on vaccination rate
        for node in G.nodes():
            G.nodes[node]['vaccinated'] = custom_vaccination(node)
            # Recalculate risk factor with new vaccination status
            G.nodes[node]['risk_factor'] = calculate_risk_factor(
                G.nodes[node]['age'],
                G.nodes[node]['vaccinated']
            )
        
        # Prepare simulation parameters
        simulation_params = {
            'max_days': simulation_days,
            'infection_prob': transmission_rate * (1 - mask_usage * 0.5),  # Mask effectiveness reduces transmission
            'hospitalization_prob': hospitalization_rate,
            'death_prob': mortality_rate,
            'recovery_time': max(1, int(1 / recovery_rate)),  # Ensure at least 1 day
            'hospital_recovery_time': max(1, int(1 / recovery_rate) * 1.5),  # Longer recovery time for hospitalized
            'mask_effectiveness': mask_usage
        }
        
        # Run simulation
        timeline, status_history = simulate_sihrd(
            G,
            status,
            infection_day,
            hospitalization_day,
            simulation_params
        )
        
        # Calculate final statistics
        final_stats = {
            'total_infected': timeline['infected'][-1] + timeline['hospitalized'][-1] + timeline['recovered'][-1] + timeline['deceased'][-1],  # All people who have ever been infected
            'total_recovered': timeline['recovered'][-1],  # Current recovered
            'total_deceased': timeline['deceased'][-1],  # Current deceased
            'peak_infected': max(timeline['infected']),
            'peak_hospitalized': max(timeline['hospitalized']),
            'average_risk_factor': float(np.mean([G.nodes[node]['risk_factor'] for node in G.nodes()])),
            'average_age': float(np.mean([G.nodes[node]['age'] for node in G.nodes()]))
        }
        
        # Compute 2D positions for each node using spring_layout
        pos = nx.spring_layout(G, seed=42)
        
        # Convert results to JSON-serializable format
        formatted_results = {
            "timeline": {
                "susceptible": [float(x) for x in timeline["susceptible"]],
                "infected": [float(x) for x in timeline["infected"]],
                "hospitalized": [float(x) for x in timeline["hospitalized"]],
                "recovered": [float(x) for x in timeline["recovered"]],
                "deceased": [float(x) for x in timeline["deceased"]]
            },
            "network_states": [
                {str(k): v.value for k, v in state.items()}
                for state in status_history
            ],
            "network_structure": {
                "nodes": [
                    {"id": str(node), "x": float(pos[node][0]), "y": float(pos[node][1])}
                    for node in G.nodes()
                ],
                "edges": [
                    {"source": str(edge[0]), "target": str(edge[1])}
                    for edge in G.edges()
                ]
            },
            "final_stats": final_stats,
            "age_distribution": {
                "data": [{
                    "type": "histogram",
                    "x": [G.nodes[node]['age'] for node in G.nodes()],
                    "name": "Age Distribution",
                    "marker": {"color": "#3498db"},
                    "opacity": 0.7,
                    "nbinsx": 20
                }],
                "layout": {
                    "title": {"text": "Population Age Distribution", "font": {"size": 24}},
                    "xaxis": {"title": {"text": "Age (years)"}, "showgrid": True},
                    "yaxis": {"title": {"text": "Number of Individuals"}, "showgrid": True},
                    "showlegend": False
                }
            },
            "risk_distribution": {
                "data": [{
                    "type": "histogram",
                    "x": [G.nodes[node]['risk_factor'] for node in G.nodes()],
                    "name": "Risk Factor Distribution",
                    "marker": {"color": "#e74c3c"},
                    "opacity": 0.7,
                    "nbinsx": 20
                }],
                "layout": {
                    "title": {"text": "Population Risk Factor Distribution", "font": {"size": 24}},
                    "xaxis": {"title": {"text": "Risk Factor"}, "showgrid": True},
                    "yaxis": {"title": {"text": "Number of Individuals"}, "showgrid": True},
                    "showlegend": False
                }
            },
            "infection_rates": {
                "data": [{
                    "type": "scatter",
                    "x": list(range(len(timeline['infected']))),
                    "y": [float(infected) / float(total) if total > 0 else 0 for infected, total in zip(timeline['infected'], timeline['susceptible'])],
                    "name": "Daily Infection Rate",
                    "line": {"color": "#2ecc71", "width": 2},
                    "fill": "tozeroy",
                    "fillcolor": "rgba(46, 204, 113, 0.2)"
                }],
                "layout": {
                    "title": {"text": "Daily Infection Rate", "font": {"size": 24}},
                    "xaxis": {"title": {"text": "Day"}, "showgrid": True},
                    "yaxis": {
                        "title": {"text": "Infection Rate"},
                        "showgrid": True,
                        "tickformat": ".2%"
                    },
                    "showlegend": False
                }
            }
        }
        
        return formatted_results
    
    except Exception as e:
        print(f"Simulation error: {str(e)}")  # Add logging
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/network-info")
async def get_network_info(num_nodes: int, edges_per_node: int):
    try:
        G = generate_social_network(num_nodes, edges_per_node)
        return {
            "num_nodes": G.number_of_nodes(),
            "num_edges": G.number_of_edges(),
            "average_degree": sum(dict(G.degree()).values()) / G.number_of_nodes()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 