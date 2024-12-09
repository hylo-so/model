import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple, Dict

def generate_monte_carlo_price_paths(
    file_path: str, 
    beta: float = 1, 
    T: int = 10000, 
    N: int = 1,
    decay_factor: float = 0.994  # Higher = slower decay, e.g., 0.94 gives ~6 months half-life
) -> np.ndarray:
    """
    Generate Monte Carlo price paths using Student's t-distribution fitted to historical data,
    with exponential weighting to emphasize recent data.
    
    Args:
        file_path: Path to historical price data CSV
        beta: Volatility scaling factor
        T: Number of time steps to simulate
        N: Number of paths to simulate
        decay_factor: Exponential decay factor for weighting historical data
        
    Returns:
        price_paths: Array of simulated price paths
    """
    # Analyze historical data
    historical_data = pd.read_csv(file_path)
    historical_data['Price'] = historical_data['Price'].replace(',', '', regex=True).astype(float)
    returns = historical_data['Price'].pct_change().dropna()
    current_price = historical_data['Price'].iloc[-1]
    
    # Calculate weights for historical data (more recent = higher weight)
    weights = np.power(decay_factor, np.arange(len(returns)-1, -1, -1))
    weights = weights / weights.sum()  # Normalize weights
    
    # Calculate weighted statistics
    weighted_mean = np.average(returns, weights=weights)
    weighted_var = np.average((returns - weighted_mean)**2, weights=weights)
    weighted_std = np.sqrt(weighted_var) * beta
    
    # Calculate weighted kurtosis
    weighted_kurtosis = np.average(
        ((returns - weighted_mean)/weighted_std)**4, 
        weights=weights
    ) - 3  # Subtract 3 to match scipy.stats.kurtosis definition
    
    # Find optimal degrees of freedom with weighted samples
    dfs = np.arange(2.1, 10, 0.1)
    kurtosis_differences = []
    
    for df in dfs:
        # Generate more samples for recent periods
        n_samples = int(len(returns) * 1.5)  # Generate extra samples for better estimation
        t_samples = stats.t.rvs(df, size=n_samples)
        t_kurtosis = stats.kurtosis(t_samples)
        kurtosis_differences.append(abs(t_kurtosis - weighted_kurtosis))
    
    best_df = dfs[np.argmin(kurtosis_differences)]
    
    
    # Generate price paths using weighted parameters
    t_scaled_returns = stats.t.rvs(
        df=best_df,
        loc=weighted_mean,
        scale=weighted_std,
        size=(T, N)
    )
    
    price_paths = np.zeros_like(t_scaled_returns)
    price_paths[0] = current_price
    for t in range(1, T):
        price_paths[t] = price_paths[t-1] * (1 + t_scaled_returns[t])
    
    return price_paths

