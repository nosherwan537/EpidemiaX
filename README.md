# EpidemiaX - Advanced Disease Spread Simulator

EpidemiaX is a sophisticated disease spread simulation tool that models the progression of infectious diseases through a population network. It implements an enhanced SIHRD (Susceptible, Infected, Hospitalized, Recovered, Deceased) model with realistic parameters and interactive visualizations.

## Features

- Advanced SIHRD epidemiological model
- Age-based risk factors
- Vaccination status effects
- Proximity-based transmission
- Hospital capacity simulation
- Interactive visualizations
- Network analysis
- Demographic insights
- Real-time simulation updates

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/EpidemiaX.git
cd EpidemiaX
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Web Interface (Recommended)

Run the Streamlit web application:
```bash
streamlit run app.py
```

This will open a web browser with an interactive interface where you can:
- Adjust simulation parameters
- View real-time disease spread
- Analyze demographic data
- Explore network visualizations

### Command Line Interface

Alternatively, you can run the simulation from the command line:
```bash
python main.py
```

This will:
1. Generate a social network
2. Initialize the population with various attributes
3. Run the SIHRD simulation
4. Create visualizations and save them to files

## Model Parameters

- **Population Size**: Number of individuals in the network
- **Average Connections**: Average number of connections per person
- **Initial Infected**: Percentage of initially infected population
- **Base Infection Probability**: Probability of transmission per contact
- **Recovery Time**: Average days until recovery
- **Hospital Recovery Time**: Average days in hospital
- **Hospitalization Probability**: Chance of requiring hospitalization
- **Death Probability**: Base probability of death for hospitalized cases

## Visualization Types

1. **Disease Spread Timeline**
   - Interactive plot showing SIHRD progression
   - Real-time updates during simulation

2. **Demographic Analysis**
   - Age distribution by disease status
   - Risk factor distribution
   - Vaccination impact analysis
   - Age group infection rates

3. **Network Visualization**
   - Interactive network graph
   - Node coloring by status
   - Animation of disease spread
   - Network statistics

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 