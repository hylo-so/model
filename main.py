import pandas as pd
import numpy as np

file_path = './Solana Historical Data.csv' 
new_sol_price_data = pd.read_csv(file_path)

#np.random.seed(42)

# Convert 'Date' to a datetime object
new_sol_price_data['Date'] = pd.to_datetime(new_sol_price_data['Date'])

# Sort the data by 'Date'
new_sol_price_data.sort_values('Date', inplace=True)

# Reset the index of the DataFrame after sorting
new_sol_price_data.reset_index(drop=True, inplace=True)

# Limit the DataFrame to the first 10 rows
new_sol_price_data = new_sol_price_data.head(1000)

#####################CALCULATION#####################


# Initialize the first SOL price from the CSV data
pSOL_initial = new_sol_price_data['Price'].iloc[0]

# Initial conditions setup function
def initialize_simulation():
    global nSOL, nF, nX, pF, pX
    nSOL = 300  # SOL in reserve
    pF = 1  # Price of fSOL, starts at 1
    pX = 1  # Price of xSOL, starts at 1
    
    # Calculate nF and nX based on the initial SOL reserve and prices
    nF = (pSOL_initial * nSOL) / 2
    nX = nF

# Call this function to set initial conditions before the simulation starts
initialize_simulation()

# Now, nF and nX are calculated based on the initial conditions and pSOL_initial
print(f"Initial nF: {nF}, Initial nX: {nX}, Initial pSOL: {pSOL_initial}")


# Function to calculate new pX given a change in pSOL
def calculate_new_pX(pSOL_new):
    total_value_initial = nSOL * pSOL_initial  # Initial total value of the reserve
    total_value_new = nSOL * pSOL_new  # New total value of the reserve
    
    # Since pF is always 1, we only need to adjust pX to maintain the invariant
    # nSOL * pSOL = nF * pF + nX * pX
    # Solve for pX: pX = (total_value_new - nF * pF) / nX
    pX_new = (total_value_new - nF * pF) / nX
    return pX_new

def adjust_SOL_reserve(amount_in_dollars, pSOL_current):
    global nSOL  # Access the global SOL reserve variable
    SOL_change = amount_in_dollars / pSOL_current  # Calculate the SOL equivalent of the dollar amount
    nSOL += SOL_change  # Adjust the SOL reserve by the SOL equivalent

def mint_fSOL(amount, pSOL_current):
    global nF
    nF += amount  # Increase or decrease fSOL supply
    amount_in_dollars = amount * pF  # Calculate the dollar value of the amount
    adjust_SOL_reserve(amount_in_dollars, pSOL_current)  # Adjust the SOL reserve

def mint_xSOL(amount, pSOL_current):
    global nX
    nX += amount  # Increase or decrease xSOL supply
    amount_in_dollars = amount * pX  # Calculate the dollar value based on the current pX
    adjust_SOL_reserve(amount_in_dollars, pSOL_current)  # Adjust the SOL reserve

# Function to recalculate pX after minting/burning, given the current SOL price
def recalculate_pX_after_mint_burn(pSOL_current):
    total_value_current = nSOL * pSOL_current
    pX_new_after_mint_burn = (total_value_current - (nF * pF)) / nX
    return pX_new_after_mint_burn


# Function to calculate market caps and collateralization ratio
def calculate_market_caps_and_collateral_ratio(pSOL_current):
    # Calculate market cap of fSOL and xSOL
    market_cap_fSOL = nF * pF
    market_cap_xSOL = nX * pX  # Note: pX should be updated to the latest calculated value
    
    # Calculate collateralization ratio for fSOL
    total_SOL_reserve_in_dollars = nSOL * pSOL_current
    collateralization_ratio_fSOL = total_SOL_reserve_in_dollars / market_cap_fSOL
    
    return market_cap_fSOL, market_cap_xSOL, collateralization_ratio_fSOL

#####################LOOP#####################

daily_data = []

# Set the initial SOL price for simulation purposes
pSOL_current = new_sol_price_data['Price'].iloc[0]  # Initial SOL price from the new data

# Simulation parameters
days = len(new_sol_price_data)  # Adjust the simulation length to match the SOL price data length

def calculate_collateral_ratio(nSOL, pSOL_current, nF, pF, nX, pX):
    # Calculate the total value of the SOL reserve
    total_SOL_value = nSOL * pSOL_current
    
    # Calculate the market cap of fSOL and xSOL
    market_cap_fSOL = nF * pF

    market_cap_xSOL = nX * pX
    
    # Calculate the collateralization ratio for fSOL
    collateralization_ratio_fSOL = total_SOL_value / market_cap_fSOL  # Multiply by 100 to express as a percentage
    
    return collateralization_ratio_fSOL

def adjust_fSOL_to_target_CR(pSOL_current, nX, pX, target_CR=1.3):
    global nF, nSOL, pF
    # Calculate nF_required to achieve the target collateral ratio
    nF_required = (nX * pX) / (pF * (target_CR - 1))
    # Calculate the adjustment needed
    fSOL_adjustment = nF_required - nF

    return fSOL_adjustment

def use_stability_pool(pSOL_current):
    global nF, nSOL, nX, pF, pX
    # Calculate if and how much fSOL needs to be adjusted to reach the target CR of 1.3
    fSOL_adjustment = adjust_fSOL_to_target_CR(pSOL_current, nX, pX, target_CR=1.3)
    
    # Ensure that fSOL adjustment is zero if it's positive, since we're only considering burning fSOL
    fSOL_adjustment = fSOL_adjustment if fSOL_adjustment <= 0 else 0

    if fSOL_adjustment < 0:
        # If adjustment is negative, it indicates the need to burn some fSOL to reduce nF
        max_fSOL_to_burn = nF * 0.5  # Calculate 50% of the current fSOL supply
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
    elif 1.5 < collateral_ratio <= 2.2:
        return {'fSOL_mint': 0.60, 'xSOL_mint': 0.85}
    elif 1 < collateral_ratio <= 1.5:
        return {'fSOL_mint': 0.00, 'xSOL_mint': 0.95}
    else:
        # Define behavior for < 100% collateral ratio if needed
        return {'fSOL_mint': 0.00, 'xSOL_mint': 1.00}
    
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
                'xSOL_mint_amount': np.random.normal(0.04, 0.07), 
                'fSOL_burn_amount': np.random.normal(0.04, 0.07), 
                'xSOL_burn_amount': np.random.normal(0.01, 0.03)}
    elif 1 < collateral_ratio <= 1.5:
        return {'fSOL_mint_amount': np.random.normal(0.00, 0.01), 
                'xSOL_mint_amount': np.random.normal(0.05, 0.1), 
                'fSOL_burn_amount': np.random.normal(0.05, 0.1), 
                'xSOL_burn_amount': np.random.normal(0.00, 0.01)}
    else:
        # Define behavior for < 100% collateral ratio if needed
        return {'fSOL_mint_amount': np.random.normal(0.00, 0.01), 
                'xSOL_mint_amount': np.random.normal(0.05, 0.1), 
                'fSOL_burn_amount': np.random.normal(0.05, 0.1), 
                'xSOL_burn_amount': np.random.normal(0.00, 0.01)}

# Within your daily simulation loop
for day in range(days):
    pSOL_current = new_sol_price_data['Price'].iloc[day]  # Update current SOL price
    

    # Update pX for the current day before calculating the collateral ratio
    pX = recalculate_pX_after_mint_burn(pSOL_current)
    
    # Recalculate the collateral ratio after adjustment
    collateral_ratio = calculate_collateral_ratio(nSOL, pSOL_current, nF, pF, nX, pX)
    
    
    # Get the action probabilities for the current collateral ratio
    probabilities = get_action_probabilities(collateral_ratio)
    
    # Decide actions for fSOL and xSOL based on the probabilities
    action_fSOL = 'mint' if np.random.rand() < probabilities['fSOL_mint'] else 'burn'
    action_xSOL = 'mint' if np.random.rand() < probabilities['xSOL_mint'] else 'burn'
    
    # Determine mint/burn amount
    amount_to_mint = get_mint_amount(collateral_ratio)
    fSOL_to_mint = amount_to_mint['fSOL_mint_amount']
    xSOL_to_mint = amount_to_mint['xSOL_mint_amount']
    fSOL_to_burn = amount_to_mint['fSOL_burn_amount']
    xSOL_to_burn = amount_to_mint['xSOL_burn_amount']

    mint_amount_fSOL = int(nF*fSOL_to_mint) 
    mint_amount_xSOL = int(nX*xSOL_to_mint) 
    burn_amount_fSOL = int(nF*fSOL_to_burn)
    burn_amount_xSOL = int(nX*xSOL_to_burn)
   
    # Adjust the mint/burn amount based on the decided action
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

    stability_pool = use_stability_pool(pSOL_current)
    
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
        "Collaterization ratio": calculate_collateral_ratio(nSOL, pSOL_current, nF, pF, nX, pX)
    }

    # Append the day's data to the list
    daily_data.append(day_data)

# After the loop, convert the list of dictionaries to a DataFrame
results_df = pd.DataFrame(daily_data)

# Write the DataFrame to a CSV file
results_csv_path = './simulation_results.csv'  # Update this path
results_df.to_csv(results_csv_path, index=False)

print(f"Simulation results have been written to {results_csv_path}")

