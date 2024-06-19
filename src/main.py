from itertools import product
import pandas as pd
import numpy as np
import configparser
import os
import shutil
from modelisation.run_hylo_simulations import run_hylo_simulations
from modelisation.utils.monteCarlo import generate_monte_carlo_price_paths
from typing import List, Tuple

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

def clear_output_directory(directory_path: str):
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

# Determine the number of decimal places in sModeStep
def count_decimal_places(value):
    text = str(value)
    if '.' in text:
        return len(text.split('.')[1])
    return 0

decimal_places = count_decimal_places(sModeStep)

def simulate(
    file_path: str,
    beta: float,
    T: int,
    N: int,
    stab_mod_fSOL_SOL_range: np.ndarray,
    stab_mod_fee_control_range: np.ndarray,
    num_runs_per_path: int,
    stab_mod_fSOL_xSOL_range: np.ndarray,
) -> None:
    stability_thresholds: List[Tuple[float, float, float]] = [
        (round(fSOL_SOL, decimal_places), round(fee_control, decimal_places), round(fSOL_xSOL, decimal_places))
        for fSOL_SOL, fee_control, fSOL_xSOL in product(stab_mod_fSOL_SOL_range, stab_mod_fee_control_range, stab_mod_fSOL_xSOL_range)
        if fSOL_SOL <= fee_control or fSOL_xSOL <= fee_control
    ]
    total_iterations = len(stability_thresholds) * N
    run_id = 1
    
    for i in range(N):
        price_paths = generate_monte_carlo_price_paths(file_path, beta, T, 1)
        
        for (current_iteration, (stab_mod_fSOL_SOL, stab_mod_fee_control, stab_mod_fSOL_xSOL)) in enumerate(stability_thresholds, start=1):
            print(f"Running simulation {i * len(stability_thresholds) + current_iteration}/{total_iterations}")
            
            # Run simulations
            run_hylo_simulations(
                price_paths,
                stab_mod_fSOL_SOL,
                stab_mod_fee_control,
                stab_mod_fSOL_xSOL,
                num_runs_per_path=num_runs_per_path,
                run_id=run_id,
            )
        run_id += 1
             
    print("All simulations completed.")

# Clear the output directory once at the start
clear_output_directory(output_directory)


simulate(file_path, beta, T, N, stab_mod_fSOL_SOL_range, stab_mod_fee_control_range, num_runs_per_path, stab_mod_fSOL_xSOL_range)
