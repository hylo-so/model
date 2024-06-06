import numpy as np
from monteCarlo import generate_monte_carlo_price_paths
from hyloModelisation import Simulation

sim = Simulation()

#np.random.seed(541)

np.random.seed(5422)


# Specify the path to your historical data CSV
file_path = '../Solana Historical Data.csv'

####INPUT####
T = 1000 # Number of day in each montecarlo simulation
N = 1 # Number of simulation created
beta = 1.0 # Beta inferior to 1 reflect lower volatility and superior to 1 it reflect higher volatility
stab_mod_fSOL_SOL = 1.2# Stability mode 1 collaterization ratio threshold, usage of stability pool  
stab_mod_fee_control = 1.5 # Stability mode 2 collaterization ratio threshold, mint of fSOL disable  stab_mod_fee_control
stab_mod_fSOL_xSOL = 1.3 # Stability mode 3 collaterization ratio threshold, usage of stability pool 2
VaR_confidence_level = 0.999
num_runs_per_path = 1  # Define how many times to run the simulation per price path


results = generate_monte_carlo_price_paths(file_path, beta, T, N, VaR_confidence_level)
price_paths, var_percentile = results
all_runs_results = []



# Assuming 'price_paths' is a 2D array where each column is a different simulation run
for path_index, path in enumerate(price_paths.T):  # Transpose to iterate over each simulation run as a separate array
    path_results = []  # Store results for each run of this path
    
    for run in range(num_runs_per_path):
        run_result = sim.run_simulation(path, stab_mod_fSOL_SOL, stab_mod_fee_control, stab_mod_fSOL_xSOL)  # Run the simulation with the current path
        path_results.append(run_result)  # Collect results for this run
    
    all_runs_results.append(path_results)  # Store all runs for this path

    print(f"Completed simulations for path {path_index + 1}/{price_paths.shape[1]}")

# Initialize counters for aggregation
total_stability_pool_fSOL_SOL_non_zero = 0
total_stability_pool_fSOL_xSOL_non_zero = 0
total_xSOL_negative_price = 0
total_runs = 0

# Iterate over each set of results for the paths
for path_results in all_runs_results:
    for result in path_results:
        total_stability_pool_fSOL_SOL_non_zero += result[0]
        total_xSOL_negative_price += result[1]
        avg_collateral_ratio = result[2]/ num_runs_per_path
        total_stability_pool_fSOL_xSOL_non_zero += result[3]
    total_runs += len(path_results)

# Calculate averages
average_stability_pool_fSOL_SOL_non_zero = total_stability_pool_fSOL_SOL_non_zero / total_runs / T *100
average_stability_pool_fSOL_xSOL_non_zero = total_stability_pool_fSOL_xSOL_non_zero / total_runs / T *100
average_xSOL_negative_price = total_xSOL_negative_price / total_runs / T * 100
average_xSOL_negative_price_run = (total_xSOL_negative_price / total_runs) * 100

print(f"Average times stability pool fSOL SOL returned non-zero: {average_stability_pool_fSOL_SOL_non_zero}%")
print(f"Average times stability pool fSOL xSOL returned non-zero: {average_stability_pool_fSOL_xSOL_non_zero}%")
print(f"Percentage of runs experiencing collateralization failure: {average_xSOL_negative_price_run}%")
print(f"Average percentage of days with a negative xSOL price across all simulations: {average_xSOL_negative_price}%")
#print (f"VaR with confidence level of {VaR_confidence_level}:", var_percentile,"%")
