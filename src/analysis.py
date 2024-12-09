import pandas as pd
import glob
import re
from pathlib import Path
import configparser
import sys

def analyze_depeg_events():
    # Read config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Get expected number of time steps from config
    expected_T = config.getint('settings', 'T')
    hyUSD_SOL_staked = config.getfloat('settings', 'hyUSD_staked_per')
    
    # Get all CSV files in output directory
    files = glob.glob('./src/output/simulations/run_*.csv')
    
    # Debug output
    print("\nDebug Information:")
    print(f"Expected timesteps (T) from config: {expected_T}")
    print(f"Number of files found: {len(files)}")
    
    # Check each file's length
    file_lengths = {}
    incomplete_files = []
    for file in files:
        try:
            df = pd.read_csv(file)
            file_lengths[Path(file).name] = len(df)
            if len(df) < expected_T:
                incomplete_files.append((Path(file).name, len(df)))
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    if not files:
        print("No CSV files found in the output directory")
        return None, None
    
    # Pattern depends on whether SOL staking is enabled
    if hyUSD_SOL_staked == 0:
        pattern = r'run_(\d+\.\d+)-PATH_(\d+)-SOL_\d+\.\d+-FEE_(\d+\.\d+)-xSOL_(\d+\.\d+)\.csv'
    else:
        pattern = r'run_(\d+\.\d+)-PATH_(\d+)-SOL_(\d+\.\d+)-FEE_(\d+\.\d+)-xSOL_(\d+\.\d+)\.csv'
    
    results = []
    invalid_files = []
    
    for file in files:
        try:
            df = pd.read_csv(file)
            filename = Path(file).name
            
            match = re.match(pattern, filename)
            if match:
                if hyUSD_SOL_staked == 0:
                    run_id, path_id, fee_param, xsol_param = match.groups()
                    result_dict = {
                        'run_id': float(run_id),
                        'path_id': int(path_id),
                        'fee_param': float(fee_param),
                        'xsol_param': float(xsol_param),
                    }
                else:
                    run_id, path_id, sol_param, fee_param, xsol_param = match.groups()
                    result_dict = {
                        'run_id': float(run_id),
                        'path_id': int(path_id),
                        'sol_param': float(sol_param),
                        'fee_param': float(fee_param),
                        'xsol_param': float(xsol_param),
                    }
                
                # Check for depeg: either CR < 1 or simulation stopped early
                depeg_event = (df['collateralization_ratio_post_stab_SOL'] < 1).any() or len(df) < expected_T
                result_dict['depeg_event'] = depeg_event
                
                results.append(result_dict)
            else:
                invalid_files.append(filename)
        except Exception as e:
            print(f"\nError processing file {file}: {str(e)}")
            invalid_files.append(filename)
    
    if invalid_files:
        print("\nWarning: The following files could not be processed:")
        for file in invalid_files:
            print(f"- {file}")
    
    if not results:
        print("\nNo valid results found")
        return None, None

    results_df = pd.DataFrame(results)
    
    # Define grouping columns based on SOL staking
    if hyUSD_SOL_staked == 0:
        grouping_cols = ['xsol_param', 'fee_param']
    else:
        grouping_cols = ['xsol_param', 'sol_param', 'fee_param']
    
    # Group by parameters and aggregate
    param_analysis = results_df.groupby(grouping_cols).agg({
        'depeg_event': ['count', 'sum', 'mean']
    }).round(3)
    
    # Reset index and sort
    param_analysis = param_analysis.reset_index()
    param_analysis = (param_analysis.sort_values(['xsol_param', 'fee_param'])
                     .set_index(['xsol_param', 'fee_param']))
    
    return results_df, param_analysis

def analyze_stability_pool_usage():
    # Read config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Get expected number of time steps from config
    expected_T = config.getint('settings', 'T')
    hyUSD_SOL_staked = config.getfloat('settings', 'hyUSD_staked_per')
    
    # Get all CSV files in output directory
    files = glob.glob('./src/output/simulations/run_*.csv')
    
    if not files:
        print("No CSV files found in the output directory")
        return None, None
    
    # Pattern depends on whether SOL staking is enabled
    if hyUSD_SOL_staked == 0:
        pattern = r'run_(\d+\.\d+)-PATH_(\d+)-SOL_\d+\.\d+-FEE_(\d+\.\d+)-xSOL_(\d+\.\d+)\.csv'
    else:
        pattern = r'run_(\d+\.\d+)-PATH_(\d+)-SOL_(\d+\.\d+)-FEE_(\d+\.\d+)-xSOL_(\d+\.\d+)\.csv'
    
    results = []
    invalid_files = []
    
    print("\nAnalyzing Stability Pool Usage...")
    print(f"Number of files found: {len(files)}")
    
    for file in files:
        try:
            df = pd.read_csv(file)
            filename = Path(file).name
            
            match = re.match(pattern, filename)
            if match:
                if hyUSD_SOL_staked == 0:
                    run_id, path_id, fee_param, xsol_param = match.groups()
                else:
                    run_id, path_id, sol_param, fee_param, xsol_param = match.groups()
                
                # Count stability pool activations
                sol_activations = (df['stab_SOL_nF_burned'] > 0).sum()
                xsol_activations = (df['stab_xSOL_nF_burned'] > 0).sum()
                total_activations = sol_activations + xsol_activations
                
                result = {
                    'run_id': float(run_id),
                    'path_id': int(path_id),
                    'fee_param': float(fee_param),
                    'xsol_param': float(xsol_param),
                    'run_duration': len(df),
                    'sol_pool_activations': sol_activations,
                    'xsol_pool_activations': xsol_activations,
                    'total_pool_activations': total_activations
                }
                
                if hyUSD_SOL_staked > 0:
                    result['sol_param'] = float(sol_param)
                
                results.append(result)
                
        except Exception as e:
            print(f"\nError processing file {filename}: {str(e)}")
            invalid_files.append(filename)
            continue
    
    if invalid_files:
        print("\nWarning: The following files could not be processed:")
        for file in invalid_files:
            print(f"- {file}")
    
    if not results:
        print("\nNo valid results found")
        return None, None

    results_df = pd.DataFrame(results)
    
    # Define grouping columns based on SOL staking
    if hyUSD_SOL_staked == 0:
        grouping_cols = ['xsol_param', 'fee_param']
    else:
        grouping_cols = ['xsol_param', 'sol_param', 'fee_param']
    
    # Group by parameters and aggregate
    param_analysis = results_df.groupby(grouping_cols).agg({
        'run_duration': ['mean'],
        'sol_pool_activations': ['sum', 'mean'],
        'xsol_pool_activations': ['sum', 'mean'],
        'total_pool_activations': ['sum', 'mean']
    }).round(3)
    
    # Reset index and sort
    param_analysis = param_analysis.reset_index()
    param_analysis = (param_analysis.sort_values(['xsol_param', 'fee_param'])
                     .set_index(['xsol_param', 'fee_param']))
    
    return results_df, param_analysis

def combine_and_save_analysis():
    # Run both analyses
    depeg_results, depeg_analysis = analyze_depeg_events()
    stability_results, stability_analysis = analyze_stability_pool_usage()
    
    if depeg_results is None or stability_results is None:
        print("Error: One or both analyses failed to produce results")
        return
    
    # Merge the results based on common columns (run_id, path_id, fee_param, xsol_param)
    merge_columns = ['run_id', 'path_id', 'fee_param', 'xsol_param']
    if 'sol_param' in depeg_results.columns:
        merge_columns.append('sol_param')
    
    combined_results = pd.merge(
        depeg_results,
        stability_results,
        on=merge_columns,
        suffixes=('_depeg', '_stab')
    )
    
    # Group by parameters and create summary
    grouping_cols = ['xsol_param', 'fee_param']
    if 'sol_param' in combined_results.columns:
        grouping_cols.append('sol_param')
        
    summary = combined_results.groupby(grouping_cols).agg({
        'depeg_event': ['count', 'sum', 'mean'],
        'sol_pool_activations': ['sum', 'mean'],
        'xsol_pool_activations': ['sum', 'mean'],
        'total_pool_activations': ['sum', 'mean']
    }).round(3)
    
    # Save both detailed and summary results
    output_dir = './src/output/analysis'
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Save detailed results
    combined_results.to_csv(f'{output_dir}/detailed_results.csv', index=False)
    print(f"\nDetailed results saved to {output_dir}/detailed_results.csv")
    
    # Save summary
    summary.to_csv(f'{output_dir}/summary_results.csv')
    print(f"Summary results saved to {output_dir}/summary_results.csv")
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print(f"Total runs analyzed: {len(combined_results)}")
    print(f"Total depegs: {combined_results['depeg_event'].sum()}")
    print(f"Depeg rate: {(combined_results['depeg_event'].mean() * 100):.2f}%")
    print(f"Total stability pool activations: {combined_results['total_pool_activations'].sum()}")
    print(f"Average activations per run: {combined_results['total_pool_activations'].mean():.2f}")
    
    return combined_results, summary

if __name__ == "__main__":
    combined_results, summary = combine_and_save_analysis()
