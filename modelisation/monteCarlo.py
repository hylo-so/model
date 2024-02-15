import numpy as np
import pandas as pd

def generate_monte_carlo_price_paths(file_path, beta=1, T=10000, N=1, confidence_level=0.95):
    # Read the historical data
    historical_data = pd.read_csv(file_path)
    historical_data['Price'] = historical_data['Price'].replace(',', '', regex=True).astype(float)
    historical_data['Daily Return'] = historical_data['Price'].pct_change()
    historical_data_cleaned = historical_data.dropna()

    # Last available price
    current_price = historical_data_cleaned['Price'].iloc[-1]

    # Statistical properties of historical daily returns
    mean_return = historical_data_cleaned['Daily Return'].mean()
    std_return = historical_data_cleaned['Daily Return'].std() * beta


    # Generate future returns for each simulation
    future_returns = np.random.normal(mean_return, std_return, (T, N))

    # Initialize and calculate the price paths
    price_paths = np.zeros_like(future_returns)
    price_paths[0] = current_price
    for t in range(1, T):
        price_paths[t] = price_paths[t-1] * (1 + future_returns[t])
    
    # Calculate daily returns for the simulation
    daily_returns = (price_paths[1:] - price_paths[:-1]) / price_paths[:-1]

    # Aggregate daily returns across all simulations to form a distribution
    aggregated_daily_returns = daily_returns.flatten()

    # Calculate daily VaR
    var_percentile = np.percentile(aggregated_daily_returns, (1 - confidence_level) * 100)

    return price_paths, var_percentile*100

