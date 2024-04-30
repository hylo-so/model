import enum
import pandas as pd
import numpy as np
import configparser
from utils.simulation_utils import (mint_fSOL, mint_xSOL, recalculate_pX, calculate_collateral_ratio, use_stability_pool)
from utils.event_distributions import (get_action_probabilities, get_mint_amount)

class Action(enum.Enum):
    MintFSOL = 1
    BurnFSOL = 2
    MintXSOL = 3
    BurnXSOL = 4
    StabilityPoolAdjustment = 5
    UpdateMarketPrices = 6

class Simulation:
    def __init__(self, config_path='config.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)
        self.config = config
        self.amount_SOL_initial = config.getint('settings', 'amount_SOL_initial')
        self.fSOL_staked_per = config.getfloat('settings', 'fSOL_staked_per')
        
        self.nSOL = self.amount_SOL_initial
        self.pF = 1
        self.pX = 1
        self.nF = None
        self.nX = None

    def initialize_simulation(self, pSOL_initial):
        self.nF = (pSOL_initial * self.nSOL) / 2
        self.nX = self.nF
            

    def handle_action(self, action, amount, pSOL_current=None):
        if action == Action.MintFSOL or action == Action.BurnFSOL:
            sign = 1 if action == Action.MintFSOL else -1
            amount_to_mint = amount*self.nF
            #print("nf= ",self.nF, "amount", amount_to_mint)
            self.nF, self.nSOL = mint_fSOL(self.nF, self.nSOL, sign * abs(amount_to_mint), self.pF, pSOL_current)
            #print("nof= ",self.nF)

        elif action == Action.MintXSOL or action == Action.BurnXSOL:
            sign = 1 if action == Action.MintXSOL else -1
            self.nX, self.nSOL = mint_xSOL(self.nX, self.nSOL, sign * abs(amount), self.pX, pSOL_current)

        elif action == Action.StabilityPoolAdjustment:
            self.nF += use_stability_pool(self.nF, self.fSOL_staked_per, amount, self.nX, self.pX, self.pF)
            return True

        elif action == Action.UpdateMarketPrices:
            self.pX = recalculate_pX(self.nSOL, pSOL_current, self.nF, self.pF, self.nX)

    def run_simulation(self, simulated_prices, stab_mod1, stab_mod2):
        daily_data = []
        self.pSOL = simulated_prices[0]
        self.__init__()
        self.initialize_simulation(self.pSOL)
        stability_pool_non_zero_count = 0
        xSOL_negative_price_count = 0
        

        for day, pSOL_current in enumerate(simulated_prices):
            self.pSOL = pSOL_current
            self.handle_action(Action.UpdateMarketPrices, 0, pSOL_current)
            collateral_ratio = calculate_collateral_ratio(self.nSOL, self.pSOL, self.nF, self.pF)
            probabilities = get_action_probabilities(collateral_ratio, stab_mod2)
            amount_to_mint_per = get_mint_amount(collateral_ratio, self.config)
        
            actions = [
                (Action.MintFSOL if np.random.rand() < probabilities['fSOL_mint'] else Action.BurnFSOL, amount_to_mint_per['fSOL_mint_amount']),
                (Action.MintXSOL if np.random.rand() < probabilities['xSOL_mint'] else Action.BurnXSOL, amount_to_mint_per['xSOL_mint_amount'])
            ]

            for action, amount in actions:
                self.handle_action(action, amount, pSOL_current)
            
            
            # Stability pool might be used every day depending on the simulation's parameters
            stability_pool = self.handle_action(Action.StabilityPoolAdjustment, stab_mod1)
            
            
            day_data = {
                "day": day,
                "pSOL": self.pSOL,
                "nSOL": self.nSOL,
                "pF": self.pF,
                "nF": self.nF,
                "pX": self.pX,
                "nX": self.nX,
                "Marketcap fSOL": self.pF * self.nF,
                "Marketcap xSOL": self.pX * self.nX,
                "Collateralization ratio": collateral_ratio
            }
            daily_data.append(day_data)

            
            # Check if the adjustment was made and it's less than zero
            if stability_pool == True:
                stability_pool_non_zero_count += 1

            # Check if xSOL value goes negative
            if self.pX * self.nX < 0: 
                xSOL_negative_price_count += 1

            # Exit the loop if pX is negative
            if self.pX < 0:
                break
            

        results_df = pd.DataFrame(daily_data)
        results_csv_path = './simulation_results.csv'
        results_df.to_csv(results_csv_path, index=False)

        return stability_pool_non_zero_count, xSOL_negative_price_count, collateral_ratio,

