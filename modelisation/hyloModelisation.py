import pandas as pd
import numpy as np
import configparser



def run_simulation(simulated_prices, stab_mod1, stab_mod2):

    config = configparser.ConfigParser()
    config.read('config.ini')
    
    amount_SOL_initial = config.getint('settings', 'amount_SOL_initial')
    fSOL_staked_per = config.getfloat('settings', 'fSOL_staked_per')



    # Initialization of Stability Pool and xSOL negative counter
    stability_pool_non_zero_count = 0
    xSOL_negative_price_count = 0


    #####################FUNCTION#####################


    # Initialize the first SOL price
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
    def adjust_fSOL_to_target_CR(nF, nX, pX, stab_mod1):
        global nSOL, pF
        # Calculate nF_required to achieve the target collateral ratio
        nF_required = (nX * pX) / (pF * (stab_mod1 - 1))
        # Calculate the adjustment needed
        fSOL_adjustment = nF_required - nF


        return fSOL_adjustment

    def use_stability_pool(pX, nF):
        global nSOL, nX, pF
        
        # Calculate if and how much fSOL needs to be adjusted to reach the target CR of 1.3
        fSOL_adjustment = adjust_fSOL_to_target_CR(nF, nX, pX, stab_mod1)
        
        # Ensure that fSOL adjustment is zero if it's positive, since we're only considering burning fSOL
        fSOL_adjustment = fSOL_adjustment if fSOL_adjustment <= 0 else 0

        if fSOL_adjustment < 0:
            # If adjustment is negative, it indicates the need to burn some fSOL to reduce nF
            max_fSOL_to_burn = nF * fSOL_staked_per  # Calculate % of the current fSOL supply available to be redeem
            fSOL_to_burn = -min(-fSOL_adjustment, max_fSOL_to_burn)  # Determine the actual amount to burn, without exceeding 50%

            return fSOL_to_burn
        
        return fSOL_adjustment
            

    # Function to adjust action probabilities based on collateral ratio
    def get_action_probabilities(collateral_ratio):
        if collateral_ratio > 5:
            return {'fSOL_mint': 1, 'xSOL_mint': 0.10}
        elif 3 < collateral_ratio <= 5:
            return {'fSOL_mint': 0.90, 'xSOL_mint': 0.25}
        elif 2.2 < collateral_ratio <= 3:
            return {'fSOL_mint': 0.8, 'xSOL_mint': 0.40}
        elif stab_mod2 < collateral_ratio <= 2.2:
            return {'fSOL_mint': 0.60, 'xSOL_mint': 0.6}
        elif 1 < collateral_ratio <= stab_mod2:
            return {'fSOL_mint': 0.00, 'xSOL_mint': 0.80} #fSOL mint disable, xSOL burn fees set at 8% and minting to 0%
        else:
            return {'fSOL_mint': 0.00, 'xSOL_mint': 1.00} # This result in an undercollaterized protocol
    
    # Function to defined the amount to mint based on the current collateral_ratio
    def get_mint_amount(collateral_ratio):
        # Determine which section of the INI file to read from based on the collateral_ratio
        if collateral_ratio > 5:
            section_prefix = 'CR5'
        elif 3 < collateral_ratio <= 5:
            section_prefix = 'CR3-5'
        elif 2.2 < collateral_ratio <= 3:
            section_prefix = 'CR22-3'
        elif 1 < collateral_ratio <= 2.2:  # Assuming stab_mod2 is within this range for this example
            section_prefix = 'CRmod2-22'
        else:  # Assuming collateral_ratio <= 1 for the 'else' case, using CR1-mod2 as a fallback
            section_prefix = 'CR1-mod2'

        # Constructing the keys to fetch the right values
        fSOL_mint_mean_key = f'{section_prefix}_fSOL_mint_mean'
        fSOL_mint_std_key = f'{section_prefix}_fSOL_mint_std'
        xSOL_mint_mean_key = f'{section_prefix}_xSOL_mint_mean'
        xSOL_mint_std_key = f'{section_prefix}_xSOL_mint_std'
        fSOL_burn_mean_key = f'{section_prefix}_fSOL_burn_mean'
        fSOL_burn_std_key = f'{section_prefix}_fSOL_burn_std'
        xSOL_burn_mean_key = f'{section_prefix}_xSOL_burn_mean'
        xSOL_burn_std_key = f'{section_prefix}_xSOL_burn_std'

        # Use the constructed keys to get values from the config
        return {
            'fSOL_mint_amount': np.random.normal(config.getfloat('mint_amount', fSOL_mint_mean_key), config.getfloat('mint_amount', fSOL_mint_std_key)), 
            'xSOL_mint_amount': np.random.normal(config.getfloat('mint_amount', xSOL_mint_mean_key), config.getfloat('mint_amount', xSOL_mint_std_key)), 
            'fSOL_burn_amount': np.random.normal(config.getfloat('mint_amount', fSOL_burn_mean_key), config.getfloat('mint_amount', fSOL_burn_std_key)), 
            'xSOL_burn_amount': np.random.normal(config.getfloat('mint_amount', xSOL_burn_mean_key), config.getfloat('mint_amount', xSOL_burn_std_key))
        }
    #####################LOOP#####################
        
    
    # Simulation start
    for day in range(days):

        # Update current SOL price
        pSOL_current = simulated_prices[day] 

        # Update pX for the current day before calculating the collateral ratio
        pX = recalculate_pX(pSOL_current)
        
        # Recalculate the collateral ratio after adjustment
        collateral_ratio_before_mb = calculate_collateral_ratio(nSOL, pSOL_current, nF, pF)
        
        # Get the action probabilities for the current collateral ratio
        probabilities = get_action_probabilities(collateral_ratio_before_mb)
        
        # Decide actions for fSOL and xSOL based on the probabilities
        action_fSOL = 'mint' if np.random.rand() < probabilities['fSOL_mint'] else 'burn'
        action_xSOL = 'mint' if np.random.rand() < probabilities['xSOL_mint'] else 'burn'
        
        # Determine mint/burn amount percentage of the current supply
        amount_to_mint = get_mint_amount(collateral_ratio_before_mb)
        fSOL_to_mint_per = amount_to_mint['fSOL_mint_amount']
        xSOL_to_mint_per = amount_to_mint['xSOL_mint_amount']
        fSOL_to_burn_per = amount_to_mint['fSOL_burn_amount']
        xSOL_to_burn_per = amount_to_mint['xSOL_burn_amount']

        # Determine absolute number of mint/burn amount 
        mint_amount_fSOL = int(nX*pX*fSOL_to_mint_per) # we base the minting amount of fSOL on current marketcap of xSOL so ensure the minting amount of fSOL get increase drasticly in case of SOL pump
        mint_amount_xSOL = int(nX*xSOL_to_mint_per) 
        burn_amount_fSOL = int(nF*fSOL_to_burn_per)
        burn_amount_xSOL = int(nX*xSOL_to_burn_per)
    
        # Adjust the mint/burn amount based on the decided action, negative number result in a burn
        if action_fSOL == 'burn':
            mint_burn_amount_fSOL = -abs(burn_amount_fSOL)
        else:
            mint_burn_amount_fSOL = abs(mint_amount_fSOL)

        if action_xSOL == 'burn':
            mint_burn_amount_xSOL = -abs(burn_amount_xSOL)
        else:
            mint_burn_amount_xSOL = abs(mint_amount_xSOL)
        
        # Perform the minting/burning actions
        mint_fSOL(mint_burn_amount_fSOL, pSOL_current)
        mint_xSOL(mint_burn_amount_xSOL, pSOL_current)

        # Check if stability pool intervention is need
        stability_pool = use_stability_pool(pX, nF)

        mint_fSOL(stability_pool, pSOL_current)

        collateral_ratio = calculate_collateral_ratio(nSOL, pSOL_current, nF, pF)


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

    return stability_pool_non_zero_count, xSOL_negative_price_count, collateral_ratio