from itertools import product
import pandas as pd
import numpy as np
import configparser
from modelisation.run_hylo_simulations import run_hylo_simulations
from modelisation.utils.monte_carlo import generate_monte_carlo_price_paths
from utils.pre_run_utils import clear_output_directory, count_decimal_places, clean_price_csv
from typing import List, Tuple, Optional

def simulate(
    file_path: str,
    beta: float,
    T: int,
    N: int,
    stab_mod_fSOL_SOL_range: np.ndarray,
    stab_mod_fee_control_range: np.ndarray,
    num_runs_per_path: int,
    stab_mod_fSOL_xSOL_range: np.ndarray,
    input_price_csv: Optional[str] = None
) -> None:
    if input_price_csv is not None:
        N = 1  # Override N to 1 if input_price_csv is provided

    stability_thresholds: List[Tuple[float, float, float]] = [
        (round(fSOL_SOL, decimal_places), round(fee_control, decimal_places), round(fSOL_xSOL, decimal_places))
        for fSOL_SOL, fee_control, fSOL_xSOL in product(stab_mod_fSOL_SOL_range, stab_mod_fee_control_range, stab_mod_fSOL_xSOL_range)
        if fSOL_SOL <= fee_control or fSOL_xSOL <= fee_control
    ]
    total_iterations = len(stability_thresholds) * N
    run_id = 1

    if input_price_csv is not None:
        price_path = clean_price_csv(input_price_csv, T)
    else:
        price_path = generate_monte_carlo_price_paths(file_path, beta, T, N)

    for i in range(N):
        
        for (current_iteration, (stab_mod_fSOL_SOL, stab_mod_fee_control, stab_mod_fSOL_xSOL)) in enumerate(stability_thresholds, start=1):
            print(f"Running simulation {i * len(stability_thresholds) + current_iteration}/{total_iterations}")
            
            # Run simulations
            run_hylo_simulations(
                price_path,
                stab_mod_fSOL_SOL,
                stab_mod_fee_control,
                stab_mod_fSOL_xSOL,
                num_runs_per_path=num_runs_per_path,
                run_id=run_id,
            )
            run_id += 1
             
    print("All simulations completed.")


# Read configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Configuration parameters
beta = config.getfloat('settings', 'beta')
T = config.getint('settings', 'T')
N = config.getint('settings', 'N')
sModeLower = config.getfloat('settings', 'sModeLower')
sModeUpper = config.getfloat('settings', 'sModeUpper')
sModeStep = config.getfloat('settings', 'sModeStep')
num_runs_per_path = config.getint('settings', 'num_runs_per_path')

# Parameters
file_path = './Solana Historical Data.csv'
stab_mod_fSOL_SOL_range = np.arange(sModeLower, sModeUpper, sModeStep)
stab_mod_fee_control_range = np.arange(sModeLower, sModeUpper, sModeStep)
stab_mod_fSOL_xSOL_range = np.arange(sModeLower, sModeUpper, sModeStep)
output_directory = './output/'

decimal_places = count_decimal_places(sModeStep)

clear_output_directory(output_directory)

# Example usage with an optional input_price_csv argument
# input_price_csv = './input_prices.csv'  Replace with your CSV file path
# simulate(file_path, beta, T, N, stab_mod_fSOL_SOL_range, stab_mod_fee_control_range, num_runs_per_path, stab_mod_fSOL_xSOL_range, input_price_csv)

# Normal usage without input_price_csv
simulate(file_path, beta, T, N, stab_mod_fSOL_SOL_range, stab_mod_fee_control_range, num_runs_per_path, stab_mod_fSOL_xSOL_range)
