# modMCPrice.py

import numpy as np
from modelisation.utils.monteCarlo import generate_monte_carlo_price_paths
from modelisation.hyloModelisation import Simulation

def run_monte_carlo_simulations(
    file_path: str,
    T: int,
    N: int,
    beta: float,
    stab_mod_fSOL_SOL: float,
    stab_mod_fee_control: float,
    stab_mod_fSOL_xSOL: float,
    num_runs_per_path: int,
    output_directory: str,
):
    sim = Simulation()

    #np.random.seed(seed)

    results = generate_monte_carlo_price_paths(file_path, beta, T, N)
    price_paths = results
    all_runs_results = []

    run_id = 0 

    # Assuming 'price_paths' is a 2D array where each column is a different simulation run
    for path_index, path in enumerate(price_paths.T):  # Transpose to iterate over each simulation run as a separate array
        path_results = []  # Store results for each run of this path
        
        for sub_run_id in range(1, num_runs_per_path + 1):
            run_result = sim.run_simulation(path, stab_mod_fSOL_SOL, stab_mod_fee_control, stab_mod_fSOL_xSOL, run_id, sub_run_id)  # Run the simulation with the current path and pass the unique run_id and sub_run_id
            path_results.append(run_result)  # Collect results for this run
            
        run_id += 1  # Increment run counter for each run

        all_runs_results.append(path_results)  # Store all runs for this path


    # Initialize counters for aggregation
    total_stability_pool_fSOL_xSOL_non_zero, total_stability_pool_fSOL_SOL_non_zero, total_stability_pool_fSOL_xSOL_nF_redeem, total_stability_pool_fSOL_SOL_nF_redeem, total_xSOL_negative_price, total_runs = 0, 0, 0, 0, 0, 0

    # Iterate over each set of results for the paths
    for path_results in all_runs_results:
        for result in path_results:
            total_stability_pool_fSOL_SOL_non_zero += result[0]
            total_xSOL_negative_price += result[1]
            avg_collateral_ratio = result[2]/ num_runs_per_path
            total_stability_pool_fSOL_xSOL_non_zero += result[3]
            total_stability_pool_fSOL_xSOL_nF_redeem += result[4]
            total_stability_pool_fSOL_SOL_nF_redeem += result[5]

        total_runs += len(path_results)

    # Calculate averages
    average_stability_pool_fSOL_xSOL_non_zero = total_stability_pool_fSOL_xSOL_non_zero / total_runs / T *100
    average_stability_pool_fSOL_SOL_non_zero = total_stability_pool_fSOL_SOL_non_zero / total_runs / T *100
    average_stability_pool_fSOL_xSOL_nF_redeem = total_stability_pool_fSOL_xSOL_nF_redeem / total_runs
    average_stability_pool_fSOL_SOL_nF_redeem = total_stability_pool_fSOL_SOL_nF_redeem / total_runs
    average_stability_pools_nF_redeem = average_stability_pool_fSOL_xSOL_nF_redeem + average_stability_pool_fSOL_SOL_nF_redeem
    average_xSOL_negative_price = total_xSOL_negative_price / total_runs / T * 100
    average_xSOL_negative_price_run = (total_xSOL_negative_price / total_runs) * 100


    return {
        'average_stability_pool_fSOL_SOL_non_zero': average_stability_pool_fSOL_SOL_non_zero,
        'average_stability_pool_fSOL_xSOL_non_zero': average_stability_pool_fSOL_xSOL_non_zero,
        'average_xSOL_negative_price_run': average_xSOL_negative_price_run,
        'average_xSOL_negative_price': average_xSOL_negative_price,
        'average_stability_pool_fSOL_xSOL_nF_redeem': average_stability_pool_fSOL_xSOL_nF_redeem,
        'average_stability_pool_fSOL_SOL_nF_redeem': average_stability_pool_fSOL_SOL_nF_redeem,
        'average_stability_pools_nF_redeem': average_stability_pools_nF_redeem
    }
