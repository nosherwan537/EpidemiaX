# main.py

from network.generate_network import generate_social_network
from visualization.plot import visualize_social_network_static



if __name__ == "__main__":
  G = generate_social_network()
visualize_social_network_static(G, num_infected=100)