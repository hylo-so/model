from modelisation.monteCarlo import generate_monte_carlo_price_paths
import matplotlib.pyplot as plt

file_path = './Solana Historical Data.csv'

def generate_charte_MC (file_path, beta, T, N):

    # Generate price paths

    price_paths = generate_monte_carlo_price_paths(file_path, beta, T, N)  # Adjust T and N as needed

    # Plotting
    plt.figure(figsize=(14, 7))  # Set figure size
    for i in range(price_paths.shape[1]):
        plt.plot(price_paths[:, i], lw=1)  # Plot each simulation path

    plt.title('Monte Carlo Simulation of Solana Price Paths')
    plt.xlabel('Days')
    plt.ylabel('Price')
    plt.show()

