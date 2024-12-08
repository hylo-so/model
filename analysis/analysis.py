import pandas as pd
import glob
import re
from pathlib import Path
import configparser

def analyze_depeg_events():
    # Get all CSV files in output directory
    files = glob.glob('../src/output/run_*.csv')
    print(f"Found {len(files)} CSV files")
    print("Example filenames:", files[:3])
    
    if not files:
        print("No CSV files found in the output directory")
        return None, None

    # Read config to check if SOL stability pool is enabled
    config = configparser.ConfigParser()
    config.read('../src/config.ini')
    hyUSD_SOL_staked = config.getfloat('settings', 'hyUSD_staked_per')
    print(f"SOL staking enabled: {hyUSD_SOL_staked > 0}")
    
    # Updated regex pattern to match the filenames
    pattern = r'run_(\d+\.\d+)-SOL_(\d+\.\d+)-FEE_(\d+\.\d+)-xSOL_(\d+\.\d+)\.csv'
    
    results = []
    for file in files:
        df = pd.read_csv(file)
        filename = Path(file).name
        print(f"\nProcessing file: {filename}")
        
        match = re.match(pattern, filename)
        if match:
            run_id, sol_param, fee_param, xsol_param = match.groups()
            
            # Check if the simulation ended early (depeg event)
            early_stop = len(df) < 365  # Assuming 365 days is full simulation
            
            results.append({
                'run_id': float(run_id),
                'sol_param': float(sol_param),
                'fee_param': float(fee_param),
                'xsol_param': float(xsol_param),
                'early_stop': early_stop,
                'days_run': len(df)
            })
        else:
            print(f"No pattern match for filename: {filename}")
    
    if not results:
        print("\nNo valid results found")
        return None, None

    results_df = pd.DataFrame(results)
    
    # Calculate statistics
    total_runs = len(results_df)
    depeg_events = results_df['early_stop'].sum()
    depeg_percentage = (depeg_events / total_runs) * 100
    
    print(f"\nTotal number of runs: {total_runs}")
    print(f"Number of depeg events: {depeg_events}")
    print(f"Percentage of runs with depeg: {depeg_percentage:.2f}%")
    
    # Group by parameters to see which combinations are more stable
    param_analysis = results_df.groupby(['sol_param', 'fee_param', 'xsol_param']).agg({
        'early_stop': ['count', 'sum', 'mean']
    }).round(3)
    
    return results_df, param_analysis

# Run the analysis
results_df, param_analysis = analyze_depeg_events()

# Display parameter combinations sorted by stability (lowest depeg rate first)
print("\nParameter combinations sorted by stability:")
print(param_analysis.sort_values(('early_stop', 'mean')))