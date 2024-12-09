import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def create_heatmaps_from_summary():
    # Read the summary results
    summary_df = pd.read_csv('./output/analysis/summary_results.csv', skiprows=[0, 1])
    
    # Rename columns to their proper names
    summary_df.columns = ['xsol_param', 'fee_param', 
                         'count', 'depeg_sum', 'depeg_mean',
                         'sol_pool_sum', 'sol_pool_mean',
                         'xsol_pool_sum', 'xsol_pool_mean',
                         'total_pool_sum', 'total_pool_mean']
    
    # Create figure with two subplots side by side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    # Prepare data for heatmaps
    depeg_data = summary_df.pivot(
        index='xsol_param', 
        columns='fee_param', 
        values='depeg_mean'
    )
    
    stability_data = summary_df.pivot(
        index='xsol_param', 
        columns='fee_param', 
        values='total_pool_mean'
    )
    
    # Create depeg heatmap
    sns.heatmap(
        depeg_data,
        ax=ax1,
        annot=True,
        fmt='.2f',
        cmap='RdYlGn_r',
        vmin=0,
        vmax=1,
        center=0.5,
        cbar_kws={'label': 'Depeg Rate'}
    )
    ax1.set_title('Depeg Event Rate')
    ax1.set_xlabel('Fee Parameter')
    ax1.set_ylabel('xSOL Parameter')
    
    # Create stability pool usage heatmap
    sns.heatmap(
        stability_data,
        ax=ax2,
        annot=True,
        fmt='.1f',
        cmap='YlOrRd',
        cbar_kws={'label': 'Average Stability Pool Activations'}
    )
    ax2.set_title('Average Stability Pool Activations')
    ax2.set_xlabel('Fee Parameter')
    ax2.set_ylabel('xSOL Parameter')
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig('./output/analysis/parameter_analysis_heatmaps.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    create_heatmaps_from_summary()