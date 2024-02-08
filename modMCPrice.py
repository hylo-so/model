import pandas as pd
import numpy as np
from monteCarlo import generate_monte_carlo_price_paths

#np.random.seed(7)

# Specify the path to your historical data CSV
file_path = './Solana Historical Data.csv'

# Generate the Monte Carlo price paths
price_paths = generate_monte_carlo_price_paths(file_path, T=1000, N=30)

def run_simulation(simulated_prices):

    
    # input
    amount_SOL_initial = 300 # Intial amount of SOL 
    stab_mod1 = 1.5 # Stability mode 1 collaterization ratio threshold, usage of stability pool
    stab_mod2 = 1.6 # Stability mode 2 collaterization ratio threshold, mint of fSOL disable
    fSOL_staked_per = 0.4 # Percentage of the fSOL supply staked in the stability Pool


    # Initialization of Stability Pool and xSOL negative counter
    stability_pool_non_zero_count = 0
    xSOL_negative_price_count = 0


    #####################FUNCTION#####################


    # Initialize the first SOL price from the CSV data
    pSOL_initial = simulated_prices[0]

    # Initial conditions setup function
    def initialize_simulation():
        global nSOL, nF, nX, pF, pX
        nSOL = amount_SOL_initial  # SOL in reserve
        pF = 1  # Price of fSOL, starts at 1
        pX = 1  # Price of xSOL, starts at 1
        
        # Calculate nF and nX based on the initial SOL reserve and prices
        nF = (pSOL_initial * nSOL) / 2
        nX = nF

    # Function to set initial conditions before the simulation starts
    initialize_simulation()

    # Adjust reserve depending on Burn and Mint
    def adjust_SOL_reserve(amount_in_dollars, pSOL_current):
        global nSOL  # Access the global SOL reserve variable
        SOL_change = amount_in_dollars / pSOL_current  # Calculate the SOL equivalent of the dollar amount
        nSOL += SOL_change  # Adjust the SOL reserve by the SOL equivalent

    def mint_fSOL(amount, pSOL_current):
        global nF
        nF += amount  # Increase or decrease fSOL supply
        amount_in_dollars = amount * pF 
        adjust_SOL_reserve(amount_in_dollars, pSOL_current) 

    def mint_xSOL(amount, pSOL_current):
        global nX
        nX += amount  # Increase or decrease xSOL supply
        amount_in_dollars = amount * pX  
        adjust_SOL_reserve(amount_in_dollars, pSOL_current)

    # Function to recalculate pX after minting/burning, given the current SOL price
    def recalculate_pX(pSOL_current):
        total_value_current = nSOL * pSOL_current
        pX_new = (total_value_current - (nF * pF)) / nX
        return pX_new



    daily_data = [] #initializing an empty list for daily data

    # Set the initial SOL price for simulation purposes
    pSOL_current = simulated_prices[0]  # Initial SOL price with first simulated price

    # Simulation parameters
    days = len(simulated_prices)  # Adjust the simulation length to match the SOL price data length

    def calculate_collateral_ratio(nSOL, pSOL_current, nF, pF):
        # Calculate the total value of the SOL reserve
        total_SOL_value = nSOL * pSOL_current
        
        # Calculate the market cap of fSOL and xSOL
        market_cap_fSOL = nF * pF

        
        # Calculate the collateralization ratio for fSOL
        collateralization_ratio_fSOL = total_SOL_value / market_cap_fSOL 
        
        return collateralization_ratio_fSOL
    

    # Calculate fSOL needed to be burn/mint to reach target CR, negative value will result in a burn
    def adjust_fSOL_to_target_CR(nX, pX, stab_mod1):
        global nF, nSOL, pF
        # Calculate nF_required to achieve the target collateral ratio
        nF_required = (nX * pX) / (pF * (stab_mod1 - 1))
        # Calculate the adjustment needed
        fSOL_adjustment = nF_required - nF


        return fSOL_adjustment

    def use_stability_pool(pX):
        global nF, nSOL, nX, pF
        
        # Calculate if and how much fSOL needs to be adjusted to reach the target CR of 1.3
        fSOL_adjustment = adjust_fSOL_to_target_CR(nX, pX, stab_mod1)
        
        # Ensure that fSOL adjustment is zero if it's positive, since we're only considering burning fSOL
        fSOL_adjustment = fSOL_adjustment if fSOL_adjustment <= 0 else 0

        if fSOL_adjustment < 0:
            # If adjustment is negative, it indicates the need to burn some fSOL to reduce nF
            max_fSOL_to_burn = nF * fSOL_staked_per  # Calculate % of the current fSOL supply available to be redeem
            fSOL_to_burn = min(-fSOL_adjustment, max_fSOL_to_burn)  # Determine the actual amount to burn, without exceeding 50%

            nF -= fSOL_to_burn  # Correctly reduce nF by the burn amount to reflect the burning of fSOL
            return fSOL_adjustment
        
        return fSOL_adjustment
            

    # Function to adjust action probabilities based on collateral ratio
    def get_action_probabilities(collateral_ratio):
        if collateral_ratio > 5:
            return {'fSOL_mint': 1, 'xSOL_mint': 0.6}
        elif 3 < collateral_ratio <= 5:
            return {'fSOL_mint': 0.90, 'xSOL_mint': 0.65}
        elif 2.2 < collateral_ratio <= 3:
            return {'fSOL_mint': 0.8, 'xSOL_mint': 0.70}
        elif stab_mod2 < collateral_ratio <= 2.2:
            return {'fSOL_mint': 0.60, 'xSOL_mint': 0.85}
        elif 1 < collateral_ratio <= stab_mod2:
            return {'fSOL_mint': 0.00, 'xSOL_mint': 0.80} #fSOL mint disable, xSOL burn fees set at 8% and minting to 0%
        else:
            return {'fSOL_mint': 0.00, 'xSOL_mint': 1.00} # This result in an undercollaterized protocol
    
    # Function to defined the amount to mint based on the current collateral_ratio
    def get_mint_amount(collateral_ratio):
        if collateral_ratio > 5:
            return {'fSOL_mint_amount': np.random.normal(0.05, 0.1), 
                    'xSOL_mint_amount': np.random.normal(0.00, 0.01), 
                    'fSOL_burn_amount': np.random.normal(0.00, 0.01), 
                    'xSOL_burn_amount': np.random.normal(0.05, 0.1)}
        elif 3 < collateral_ratio <= 5:
            return {'fSOL_mint_amount': np.random.normal(0.03, 0.08), 
                    'xSOL_mint_amount': np.random.normal(0.00, 0.02), 
                    'fSOL_burn_amount': np.random.normal(0.00, 0.02), 
                    'xSOL_burn_amount': np.random.normal(0.03, 0.08)}
        elif 2.2 < collateral_ratio <= 3:
            return {'fSOL_mint_amount': np.random.normal(0.02, 0.05), 
                    'xSOL_mint_amount': np.random.normal(0.01, 0.04), 
                    'fSOL_burn_amount': np.random.normal(0.01, 0.04), 
                    'xSOL_burn_amount': np.random.normal(0.02, 0.05)}
        elif 1.5 < collateral_ratio <= 2.2:
            return {'fSOL_mint_amount': np.random.normal(0.01, 0.03), 
                    'xSOL_mint_amount': np.random.normal(0.03, 0.05), 
                    'fSOL_burn_amount': np.random.normal(0.03, 0.05), 
                    'xSOL_burn_amount': np.random.normal(0.01, 0.03)}
        elif 1 < collateral_ratio <= 1.5:
            return {'fSOL_mint_amount': np.random.normal(0.00, 0.01), 
                    'xSOL_mint_amount': np.random.normal(0.02, 0.5), 
                    'fSOL_burn_amount': np.random.normal(0.05, 0.1), 
                    'xSOL_burn_amount': np.random.normal(0.00, 0.02)}
        else:
            return {'fSOL_mint_amount': np.random.normal(0.00, 0.01), 
                    'xSOL_mint_amount': np.random.normal(0.05, 0.1), 
                    'fSOL_burn_amount': np.random.normal(0.05, 0.1), 
                    'xSOL_burn_amount': np.random.normal(0.00, 0.01)}
        
    #####################LOOP#####################
        
    
    # Simulation start
    for day in range(days):

        # Update current SOL price
        pSOL_current = simulated_prices[day] 

        # Update pX for the current day before calculating the collateral ratio
        pX = recalculate_pX(pSOL_current)
        
        # Recalculate the collateral ratio after adjustment
        collateral_ratio = calculate_collateral_ratio(nSOL, pSOL_current, nF, pF)
        
        # Get the action probabilities for the current collateral ratio
        probabilities = get_action_probabilities(collateral_ratio)
        
        # Decide actions for fSOL and xSOL based on the probabilities
        action_fSOL = 'mint' if np.random.rand() < probabilities['fSOL_mint'] else 'burn'
        action_xSOL = 'mint' if np.random.rand() < probabilities['xSOL_mint'] else 'burn'
        
        # Determine mint/burn amount percentage of the current supply
        amount_to_mint = get_mint_amount(collateral_ratio)
        fSOL_to_mint_per = amount_to_mint['fSOL_mint_amount']
        xSOL_to_mint_per = amount_to_mint['xSOL_mint_amount']
        fSOL_to_burn_per = amount_to_mint['fSOL_burn_amount']
        xSOL_to_burn_per = amount_to_mint['xSOL_burn_amount']

        # Determine absolute number of mint/burn amount 
        mint_amount_fSOL = int(nF*fSOL_to_mint_per) # We use int to ensure it's always a positive number that is return, since we use normal distribution it can return negative number
        mint_amount_xSOL = int(nX*xSOL_to_mint_per) 
        burn_amount_fSOL = int(nF*fSOL_to_burn_per)
        burn_amount_xSOL = int(nX*xSOL_to_burn_per)
    
        # Adjust the mint/burn amount based on the decided action, negative number result in a burn
        if action_fSOL == 'burn':
            mint_burn_amount_fSOL = -abs(burn_amount_fSOL)
        else:
            mint_burn_amount_fSOL = mint_amount_fSOL

        if action_xSOL == 'burn':
            mint_burn_amount_xSOL = -abs(burn_amount_xSOL)
        else:
            mint_burn_amount_xSOL = mint_amount_xSOL
        
        # Perform the minting/burning actions
        mint_fSOL(mint_burn_amount_fSOL, pSOL_current)
        mint_xSOL(mint_burn_amount_xSOL, pSOL_current)

        # Check if stability pool intervention is need
        stability_pool = use_stability_pool(pX)

        # Update counter if stability pool is used or if xSOL is negative
        if stability_pool < 0:
            stability_pool_non_zero_count += 1
        if pX * nX < 0: 
            xSOL_negative_price_count += 1
        
        # Gather the data for the current day
        day_data = {
            "day": day,
            "pSOL": pSOL_current,
            "nSOL": nSOL,
            "value of SOL in $": pSOL_current * nSOL,
            "daily mint of fSOL": mint_burn_amount_fSOL if mint_burn_amount_fSOL > 0 else 0,
            "daily burn of fSOL": -mint_burn_amount_fSOL if mint_burn_amount_fSOL < 0 else 0,
            "daily mint of xSOL": mint_burn_amount_xSOL if mint_burn_amount_xSOL > 0 else 0,
            "daily burn of xSOL": -mint_burn_amount_xSOL if mint_burn_amount_xSOL < 0 else 0,
            "pX": pX,
            "nX": nX,
            "Marketcap xSOL": pX * nX,
            "pF": pF,
            "nF": nF,
            "Marketcap fSOL": pF * nF,
            "Total mcap": (pX * nX) + (pF * nF),
            "fSOL adjustment":  stability_pool,
            "Collaterization ratio": collateral_ratio
        }

        # Append the day's data to the list
        daily_data.append(day_data)

        if pX < 0:
            break  # Exit the loop if pX is negative

    # After the loop, convert the list of dictionaries to a DataFrame
    results_df = pd.DataFrame(daily_data)

    # Write the DataFrame to a CSV file
    results_csv_path = './simulation_results.csv' 
    results_df.to_csv(results_csv_path, index=False)

    return stability_pool_non_zero_count, xSOL_negative_price_count


all_runs_results = []
num_runs_per_path = 10  # Define how many times to run the simulation per price path

# Assuming 'price_paths' is a 2D array where each column is a different simulation run
for path_index, path in enumerate(price_paths.T):  # Transpose to iterate over each simulation run as a separate array
    path_results = []  # Store results for each run of this path
    
    for run in range(num_runs_per_path):
        run_result = run_simulation(path)  # Run the simulation with the current path
        path_results.append(run_result)  # Collect results for this run
    
    all_runs_results.append(path_results)  # Store all runs for this path

    #print(f"Completed simulations for path {path_index + 1}/{price_paths.shape[1]}")

# Initialize counters for aggregation
total_stability_pool_non_zero = 0
total_xSOL_negative_price = 0
total_runs = 0

# Iterate over each set of results for the paths
for path_results in all_runs_results:
    for result in path_results:
        total_stability_pool_non_zero += result[0]
        total_xSOL_negative_price += result[1]
    total_runs += len(path_results)

# Calculate averages
average_stability_pool_non_zero = total_stability_pool_non_zero / total_runs
average_xSOL_negative_price = total_xSOL_negative_price / total_runs

print(f"Average times stability pool returned non-zero: {average_stability_pool_non_zero}")
print(f"Average times xSOL price was negative: {average_xSOL_negative_price}")
