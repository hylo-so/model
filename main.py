from itertools import product
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from modelisation.monteCarlo import generate_monte_carlo_price_paths
from modelisation.hyloModelisation import run_simulation
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

beta = config.getfloat('settings', 'beta')
T = config.getint('settings', 'T')
N = config.getint('settings', 'N')
sModeLower = config.getfloat('settings', 'sModeLower')
sModeUpper = config.getfloat('settings', 'sModeUpper')
sModeStep = config.getfloat('settings', 'sModeStep')
num_runs_per_path = config.getint('settings', 'num_runs_per_path')

# Parameters
file_path = './Solana Historical Data.csv'
stab_mod1_range = np.arange(sModeLower, sModeUpper,sModeStep) 
stab_mod2_range = np.arange(sModeLower, sModeUpper, sModeStep)



def simulate_and_collect_data(file_path, beta, T, N, stab_mod1_range, stab_mod2_range, num_runs_per_path):
    results = []
    stability_thresholds = [(mod1, mod2) for mod1, mod2 in product(stab_mod1_range, stab_mod2_range) if mod1 <= mod2]
    total_iterations = len(stability_thresholds)
    for (current_iteration, (stab_mod1, stab_mod2)) in enumerate(stability_thresholds, start=1):
        # Print current iteration
        print(f"Running simulation {current_iteration}/{total_iterations} (stab_mod1={stab_mod1:.2f}, stab_mod2={stab_mod2:.2f})")
        # Initialize metrics
        stability_pool_counts, negative_prices_counts, collateral_ratios = [], [], []
        for _ in range(num_runs_per_path):
            # Generate price paths
            price_paths, _ = generate_monte_carlo_price_paths(file_path, beta, T, N)
            for path in price_paths.T:
                # Run the simulation with current parameters
                stability_pool_count, negative_price_count, collateral_ratio = run_simulation(path, stab_mod1, stab_mod2)
                stability_pool_counts.append(stability_pool_count)
                negative_prices_counts.append(negative_price_count)
                collateral_ratios.append(collateral_ratio)
        # Aggregate and store results
        avg_stability_pool = np.mean(stability_pool_counts)/ T * 100
        avg_negative_prices = np.mean(negative_prices_counts) * 100
        avg_collateral_ratio = np.mean(collateral_ratios)
        results.append((stab_mod1, stab_mod2, avg_stability_pool, avg_negative_prices, avg_collateral_ratio))
    return pd.DataFrame(results, columns=['stab_mod1', 'stab_mod2', 'Avg Stability Pool Non-Zero', 'Avg Negative xSOL Prices', 'Avg Collateral Ratio'])




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


