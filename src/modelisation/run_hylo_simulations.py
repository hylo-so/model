# modMCPrice.py

import numpy as np
from modelisation.utils.monteCarlo import generate_monte_carlo_price_paths
from modelisation.hyloModelisation import Simulation

def run_hylo_simulations(
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

    return 
