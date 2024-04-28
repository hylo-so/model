import pandas as pd
import numpy as np
import configparser
from modelisation.utils.simulation_utils import (adjust_SOL_reserve, mint_fSOL, mint_xSOL, recalculate_pX,
                              calculate_collateral_ratio, adjust_fSOL_to_target_CR, use_stability_pool)



class Simulation:
    def __init__(self, config_path='config.ini'):
        # Read configuration
        config = configparser.ConfigParser()
        config.read(config_path)
        self.config = config
        self.amount_SOL_initial = config.getint('settings', 'amount_SOL_initial')
        self.fSOL_staked_per = config.getfloat('settings', 'fSOL_staked_per')
        
        # Initialize the attributes for the Simulation
        self.nSOL = self.amount_SOL_initial
        self.pF = 1
        self.pX = 1
        self.nF = None
        self.nX = None

    def initialize_simulation(self, pSOL_initial):
        # Calculate nF and nX based on the initial SOL reserve and prices
        self.nF = (pSOL_initial * self.nSOL) / 2
        self.nX = self.nF

    def mint_fSOL(self, amount, pSOL_current):
        # Update nF and nSOL by minting fSOL
        self.nF, self.nSOL = mint_fSOL(self.nF, self.nSOL, amount, self.pF, pSOL_current)

    def mint_xSOL(self, amount, pSOL_current):
        # Update nX and nSOL by minting xSOL
        self.nX, self.nSOL = mint_xSOL(self.nX, self.nSOL, amount, self.pX, pSOL_current)

    def recalculate_pX(self, pSOL_current):
        # Update pX based on current market values
        self.pX = recalculate_pX(self.nSOL, pSOL_current, self.nF, self.pF, self.nX)
        return self.pX

    def calculate_collateral_ratio(self):
        # Calculate the collateral ratio
        return calculate_collateral_ratio(self.nSOL, self.pSOL, self.nF, self.pF)

    def use_stability_pool(self, stab_mod1):
        # Use stability pool to adjust fSOL holdings
        return use_stability_pool(self.nF, self.fSOL_staked_per, stab_mod1, self.nX, self.pX, self.pF)


    def get_action_probabilities(self, collateral_ratio, stab_mod2):
        if collateral_ratio > 5:
            return {'fSOL_mint': 1, 'xSOL_mint': 0.10}
        elif 3 < collateral_ratio <= 5:
            return {'fSOL_mint': 0.90, 'xSOL_mint': 0.25}
        elif 2.2 < collateral_ratio <= 3:
            return {'fSOL_mint': 0.8, 'xSOL_mint': 0.40}
        elif stab_mod2 < collateral_ratio <= 2.2:
            return {'fSOL_mint': 0.60, 'xSOL_mint': 0.6}
        elif 1 < collateral_ratio <= stab_mod2:
            return {'fSOL_mint': 0.00, 'xSOL_mint': 0.80}
        else:
            return {'fSOL_mint': 0.00, 'xSOL_mint': 1.00}

    def get_mint_amount(self, collateral_ratio):
        # Determine the section prefix based on the collateral_ratio
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
            'fSOL_mint_amount': np.random.normal(self.config.getfloat('mint_amount', fSOL_mint_mean_key), self.config.getfloat('mint_amount', fSOL_mint_std_key)), 
            'xSOL_mint_amount': np.random.normal(self.config.getfloat('mint_amount', xSOL_mint_mean_key), self.config.getfloat('mint_amount', xSOL_mint_std_key)), 
            'fSOL_burn_amount': np.random.normal(self.config.getfloat('mint_amount', fSOL_burn_mean_key), self.config.getfloat('mint_amount', fSOL_burn_std_key)), 
            'xSOL_burn_amount': np.random.normal(self.config.getfloat('mint_amount', xSOL_burn_mean_key), self.config.getfloat('mint_amount', xSOL_burn_std_key))
        }

    def run_simulation(self, simulated_prices, stab_mod1, stab_mod2):
        daily_data = []
        self.pSOL = simulated_prices[0]
        self.__init__()
        self.initialize_simulation(self.pSOL)
        stability_pool_non_zero_count = 0
        xSOL_negative_price_count = 0

        for day, pSOL_current in enumerate(simulated_prices):

            self.pSOL = pSOL_current
            self.pX = self.recalculate_pX(pSOL_current)
            collateral_ratio = self.calculate_collateral_ratio()
            probabilities = self.get_action_probabilities(collateral_ratio, stab_mod2)
            amount_to_mint = self.get_mint_amount(collateral_ratio)
            
            # Decide actions for fSOL and xSOL based on the probabilities
            action_fSOL = 'mint' if np.random.rand() < probabilities['fSOL_mint'] else 'burn'
            action_xSOL = 'mint' if np.random.rand() < probabilities['xSOL_mint'] else 'burn'
            
            # Determine mint/burn amount percentage of the current supply
            fSOL_to_mint_per = amount_to_mint['fSOL_mint_amount']
            xSOL_to_mint_per = amount_to_mint['xSOL_mint_amount']
            fSOL_to_burn_per = amount_to_mint['fSOL_burn_amount']
            xSOL_to_burn_per = amount_to_mint['xSOL_burn_amount']

            # Determine absolute number of mint/burn amount 
            mint_amount_fSOL = int(self.nX*self.pX*fSOL_to_mint_per) # we base the minting amount of fSOL on current marketcap of xSOL so ensure the minting amount of fSOL get increase drasticly in case of SOL pump
            mint_amount_xSOL = int(self.nX*xSOL_to_mint_per) 
            burn_amount_fSOL = int(self.nF*fSOL_to_burn_per)
            burn_amount_xSOL = int(self.nX*xSOL_to_burn_per)

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
            self.mint_fSOL(mint_burn_amount_fSOL, pSOL_current)
            self.mint_xSOL(mint_burn_amount_xSOL, pSOL_current)

            # Check if stability pool intervention is need
            stability_pool = self.use_stability_pool(stab_mod1)
            self.mint_fSOL(stability_pool, pSOL_current)
            collateral_ratio = self.calculate_collateral_ratio()

            # Update counter if stability pool is used or if xSOL is negative
            if stability_pool < 0:
                stability_pool_non_zero_count += 1
            if self.pX * self.nX < 0: 
                xSOL_negative_price_count += 1

            day_data = {
                "day": day,
                "pSOL": self.pSOL,
                "nSOL": self.nSOL,
                "daily mint/burn of fSOL": mint_burn_amount_fSOL,
                "daily mint/burn of xSOL": mint_burn_amount_xSOL,
                "pF": self.pF,
                "nF": self.nF,
                "pX": self.pX,
                "nX": self.nX,
                "Marketcap fSOL": self.pF * self.nF,
                "Marketcap xSOL": self.pX * self.nX,
                "fSOL adjustment":  stability_pool,
                "Collateralization ratio": collateral_ratio
            }
            daily_data.append(day_data)

            if self.pX < 0:
                break  # Exit the loop if pX is negative

            

        results_df = pd.DataFrame(daily_data)
        results_csv_path = './simulation_results.csv'
        results_df.to_csv(results_csv_path, index=False)

        return stability_pool_non_zero_count, xSOL_negative_price_count, collateral_ratio,



# Path to the CSV file
csv_file_path = 'Solana Historical Data.csv'

# Read the CSV file using pandas
data = pd.read_csv(csv_file_path)

# Extract the 'Price' column as a list
simulated_prices = data['Price'].tolist()

# Initialize the Simulation
sim = Simulation()

# Define some parameters
stab_mod1 = 1.5
stab_mod2 = 2.2

# Run the simulation with the prices extracted from the CSV
results = sim.run_simulation(simulated_prices, stab_mod1, stab_mod2)
