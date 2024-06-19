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


    results = generate_monte_carlo_price_paths(file_path, beta, T, N)
    price_paths = results
    all_runs_results = []

    run_id = 0 


    for path_index, path in enumerate(price_paths.T):
        path_results = []
        
        for sub_run_id in range(1, num_runs_per_path + 1):
            run_result = sim.run_simulation(path, stab_mod_fSOL_SOL, stab_mod_fee_control, stab_mod_fSOL_xSOL, run_id, sub_run_id)
            path_results.append(run_result) 
            
        run_id += 1 

        all_runs_results.append(path_results) 

