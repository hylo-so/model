import numpy as np
from modelisation.hyloModelisation import Simulation
from typing import List

def run_hylo_simulations(
    price_paths: np.ndarray,
    stab_mod_fSOL_SOL: float,
    stab_mod_fee_control: float,
    stab_mod_fSOL_xSOL: float,
    num_runs_per_path: int,
    run_id: int,
):
    sim = Simulation()

    for path_index, path in enumerate(price_paths.T):
        path_results = []
        
        for sub_run_id in range(1, num_runs_per_path + 1):
            run_result = sim.run_simulation(path, stab_mod_fSOL_SOL, stab_mod_fee_control, stab_mod_fSOL_xSOL, run_id, sub_run_id)
            path_results.append(run_result) 
            
