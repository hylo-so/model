from itertools import product
import pandas as pd
import numpy as np
import configparser
from model.run_hylo_simulations import run_hylo_simulations
from model.utils.monte_carlo import generate_monte_carlo_price_paths
from utils.pre_run_utils import clear_output_directory, count_decimal_places, clean_price_csv
from typing import List, Tuple, Optional

def simulate(
    file_path: str,
    beta: float,
    T: int,
    N: int,
    stab_mode_hyUSD_SOL_range: np.ndarray,
    stab_mode_fee_control_range: np.ndarray,
    num_runs_per_path: int,
    stab_mode_hyUSD_xSOL_range: np.ndarray,
    input_price_csv: Optional[str] = None
) -> None:
    if input_price_csv is not None:
        N = 1

    # Read config to check if SOL staking is enabled
    config = configparser.ConfigParser()
    config.read('config.ini')
    hyUSD_SOL_staked = config.getfloat('settings', 'hyUSD_staked_per')

    if hyUSD_SOL_staked == 0:
        # SOL staking disabled - only use fee and xSOL parameters
        stability_thresholds: List[Tuple[float, float, float]] = [
            (1.0, round(fee_control, decimal_places), round(hyUSD_xSOL, decimal_places))  # Use 1.0 as dummy SOL param
            for fee_control, hyUSD_xSOL in product(stab_mode_fee_control_range, stab_mode_hyUSD_xSOL_range)
            if hyUSD_xSOL <= fee_control  # Only check xSOL condition
        ]
    else:
        # SOL staking enabled - use all three parameters
        stability_thresholds: List[Tuple[float, float, float]] = [
            (round(hyUSD_SOL, decimal_places), round(fee_control, decimal_places), round(hyUSD_xSOL, decimal_places))
            for hyUSD_SOL, fee_control, hyUSD_xSOL in product(stab_mode_hyUSD_SOL_range, stab_mode_fee_control_range, stab_mode_hyUSD_xSOL_range)
            if hyUSD_SOL <= fee_control or hyUSD_xSOL <= fee_control
        ]

    total_iterations = len(stability_thresholds) * N
    run_id = 1

    for i in range(N):
        if input_price_csv is not None:
            price_path = clean_price_csv(input_price_csv, T)
        else:
            price_path = generate_monte_carlo_price_paths(file_path, beta, T, N=1)
        
        for (current_iteration, (stab_mode_hyUSD_SOL, stab_mode_fee_control, stab_mode_hyUSD_xSOL)) in enumerate(stability_thresholds, start=1):
            print(f"Running simulation {i * len(stability_thresholds) + current_iteration}/{total_iterations}")
            
            run_hylo_simulations(
                price_path,
                stab_mode_hyUSD_SOL,
                stab_mode_fee_control,
                stab_mode_hyUSD_xSOL,
                num_runs_per_path=num_runs_per_path,
                run_id=run_id,
                price_path_id=i+1
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
s_mode_lower = config.getfloat('settings', 's_mode_lower')
s_mode_upper = config.getfloat('settings', 's_mode_upper')
s_mode_step = config.getfloat('settings', 's_mode_step')
num_runs_per_path = config.getint('settings', 'num_runs_per_path')
hyUSD_SOL_staked = config.getfloat('settings', 'hyUSD_staked_per')

# Parameters
file_path = './Solana Historical Data.csv'
stab_mode_fee_control_range = np.arange(s_mode_lower, s_mode_upper, s_mode_step)
stab_mode_hyUSD_xSOL_range = np.arange(s_mode_lower, s_mode_upper, s_mode_step)

# Only create SOL range if staking is enabled
if hyUSD_SOL_staked > 0:
    stab_mode_hyUSD_SOL_range = np.arange(s_mode_lower, s_mode_upper, s_mode_step)
else:
    stab_mode_hyUSD_SOL_range = np.array([1.0])  # Dummy value when disabled

output_directory = './output/'
decimal_places = count_decimal_places(s_mode_step)
clear_output_directory(output_directory)

# Use historical price data
#input_price_csv = './Solana Historical Data.csv'
#simulate(file_path, beta, T, N, stab_mode_hyUSD_SOL_range, stab_mode_fee_control_range, 
#        num_runs_per_path, stab_mode_hyUSD_xSOL_range, input_price_csv=input_price_csv)

# Normal usage without input_price_csv
simulate(file_path, beta, T, N, stab_mode_hyUSD_SOL_range, stab_mode_fee_control_range, num_runs_per_path, stab_mode_hyUSD_xSOL_range)
