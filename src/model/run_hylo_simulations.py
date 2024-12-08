import numpy as np
from model.hylo_modelisation import Simulation
from typing import List

def run_hylo_simulations(
    price_paths: np.ndarray,
    stab_mode_hyUSD_SOL: float,
    stab_mode_fee_control: float,
    stab_mode_hyUSD_xSOL: float,
    num_runs_per_path: int,
    run_id: int,
    price_path_id: int,
):
    sim = Simulation()

    for path_index, path in enumerate(price_paths.T):
        
        for sub_run_id in range(1, num_runs_per_path + 1):
            sim.run_simulation(path, stab_mode_hyUSD_SOL, stab_mode_fee_control, stab_mode_hyUSD_xSOL, run_id, sub_run_id, price_path_id)

            
