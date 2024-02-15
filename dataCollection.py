import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from monteCarlo import generate_monte_carlo_price_paths
from hyloModelisation import run_simulation


def simulate_and_collect_data(file_path, beta, T, N, stab_mod1_range, stab_mod2_range, num_runs_per_path):
    results = []
    total_iterations = len(stab_mod1_range) * len(stab_mod2_range) * num_runs_per_path
    current_iteration = 0
    for stab_mod1 in stab_mod1_range:
        for stab_mod2 in stab_mod2_range:
            if stab_mod1 > stab_mod2:
                # Skip the calculation if stab_mod1 is greater than stab_mod2
                current_iteration += 1
                print(f"Running simulation {current_iteration}/{total_iterations} (stab_mod1={stab_mod1:.2f}, stab_mod2={stab_mod2:.2f})")
                continue
            # Initialize metrics
            stability_pool_counts, negative_prices_counts, collateral_ratios = [], [], []
            for _ in range(num_runs_per_path):
                # Update and print the progress
                current_iteration += 1
                print(f"Running simulation {current_iteration}/{total_iterations} (stab_mod1={stab_mod1:.2f}, stab_mod2={stab_mod2:.2f})")

                # Generate price paths
                price_paths, _ = generate_monte_carlo_price_paths(file_path, beta, T, N)
                for path in price_paths.T:
                    # Run the simulation with current parameters
                    stability_pool_count, negative_price_count, collateral_ratio = run_simulation(path, stab_mod1, stab_mod2)
                    stability_pool_counts.append(stability_pool_count)
                    negative_prices_counts.append(negative_price_count)
                    collateral_ratios.append(collateral_ratio)
            # Aggregate and store results
            avg_stability_pool = np.mean(stability_pool_counts)
            avg_negative_prices = np.mean(negative_prices_counts)
            avg_collateral_ratio = np.mean(collateral_ratios)
            results.append((stab_mod1, stab_mod2, avg_stability_pool, avg_negative_prices, avg_collateral_ratio))
    return pd.DataFrame(results, columns=['stab_mod1', 'stab_mod2', 'Avg Stability Pool Non-Zero', 'Avg Negative xSOL Prices', 'Avg Collateral Ratio'])

# Parameters
file_path = './Solana Historical Data.csv'
beta = 1
T = 1000
N = 100
stab_mod1_range = np.arange(1.3, 1.9, 0.1) 
stab_mod2_range = np.arange(1.3, 1.9, 0.1)
num_runs_per_path = 2  # Number of runs for each parameter setting


# Round to 1 decimal place
stab_mod1_range = np.round(stab_mod1_range, 1)
stab_mod2_range = np.round(stab_mod2_range, 1)

# Run simulations
results_df = simulate_and_collect_data(file_path, beta, T, N, stab_mod1_range, stab_mod2_range, num_runs_per_path)

# Save or analyze results
results_df.to_csv('./simulation_results.csv', index=False)

# Generating a heatmap for xSOL negatie
pivot_table = results_df.pivot(index="stab_mod1", columns="stab_mod2", values="Avg Negative xSOL Prices")

plt.figure(figsize=(10, 8))
sns.heatmap(pivot_table, annot=True, cmap="YlGnBu", fmt=".2f")
plt.title('Average Negative xSOL Prices Heatmap')
plt.xlabel('stab_mod2')
plt.ylabel('stab_mod1')
plt.show()

pivot_table = results_df.pivot(index="stab_mod1", columns="stab_mod2", values="Avg Stability Pool Non-Zero")

plt.figure(figsize=(10, 8))
sns.heatmap(pivot_table, annot=True, cmap="YlGnBu", fmt=".2f")
plt.title('Average stability pool usage Heatmap')
plt.xlabel('stab_mod2')
plt.ylabel('stab_mod1')
plt.show()


