from itertools import product
import pandas as pd
import numpy as np
import configparser
import os
import shutil
from modMCPrice import run_monte_carlo_simulations

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

def simulate_and_collect_data(file_path, beta, T, N, stab_mod_fSOL_SOL_range, stab_mod_fee_control_range, num_runs_per_path, stab_mod_fSOL_xSOL_range, output_directory):
    results = []
    stability_thresholds = [(fSOL_SOL, fee_control, fSOL_xSOL) for fSOL_SOL, fee_control, fSOL_xSOL in product(stab_mod_fSOL_SOL_range, stab_mod_fee_control_range, stab_mod_fSOL_xSOL_range) if fSOL_SOL <= fee_control or fSOL_xSOL <= fee_control]
    total_iterations = len(stability_thresholds)
    
    for (current_iteration, (stab_mod_fSOL_SOL, stab_mod_fee_control, stab_mod_fSOL_xSOL)) in enumerate(stability_thresholds, start=1):
        print(f"Running simulation {current_iteration}/{total_iterations} (stab_mod_fSOL_SOL={stab_mod_fSOL_SOL:.2f}, stab_mod_fee_control={stab_mod_fee_control:.2f}, stab_mod_fSOL_xSOL={stab_mod_fSOL_xSOL:.2f})")
        
        # Run simulations and collect results
        result = run_monte_carlo_simulations(
            file_path,
            T,
            N,
            beta,
            stab_mod_fSOL_SOL,
            stab_mod_fee_control,
            stab_mod_fSOL_xSOL,
            num_runs_per_path=num_runs_per_path,
            output_directory=output_directory
        )
        
        results.append((stab_mod_fSOL_SOL, stab_mod_fee_control, stab_mod_fSOL_xSOL, result['average_stability_pool_fSOL_SOL_non_zero'], result['average_xSOL_negative_price'], result['average_xSOL_negative_price_run']))
    
    return pd.DataFrame(results, columns=['stab_mod_fSOL_SOL', 'stab_mod_fee_control', 'stab_mod_fSOL_xSOL', 'Avg Stability Pool Non-Zero', 'Avg Negative xSOL Prices', 'Avg Collateral Ratio'])

# Clear the output directory once at the start
clear_output_directory(output_directory)

# Run simulations
results_df = simulate_and_collect_data(file_path, beta, T, N, stab_mod_fSOL_SOL_range, stab_mod_fee_control_range, num_runs_per_path, stab_mod_fSOL_xSOL_range, output_directory)

# Display results
print(results_df)
