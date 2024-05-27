from collections import namedtuple
import enum
import pandas as pd
import numpy as np
import configparser
from utils.simulation_utils import (mint_fSOL, mint_xSOL, recalculate_pX, calculate_collateral_ratio, use_stability_pool, use_stability_pool_2)
from utils.event_distributions import (get_action_probabilities, get_mint_amount)

class Action(enum.Enum):
    MintFSOL = 1
    BurnFSOL = 2
    MintXSOL = 3
    BurnXSOL = 4
    StabilityPoolAdjustment = 5
    StabilityPool2Adjustment = 6
    UpdateMarketPrices = 7


# Using namedtuple to define a Simulation State
SimulationState = namedtuple('SimulationState', 'nSOL pF pX nF nX')

class Simulation:
    def __init__(self, config_path='config.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)
        self.config = config
        self.amount_SOL_initial = config.getint('settings', 'amount_SOL_initial')
        self.fSOL_staked_per = config.getfloat('settings', 'fSOL_staked_per')
        self.fSOL_staked_per_2 = config.getfloat('settings', 'fSOL_staked_per_2')
   

    def initialize_simulation(self, nSOL, pSOL_initial):
        nF = (pSOL_initial * nSOL) / 2
        nX = nF
        return SimulationState(nSOL=nSOL, pF=1, pX=1, nF=nF, nX=nX)


    def handle_action(self, state, action, amount, pSOL_current=None):
        if action in [Action.MintFSOL, Action.BurnFSOL]:
            sign = 1 if action == Action.MintFSOL else -1
            new_nF, new_nSOL = mint_fSOL(state.nF, state.nSOL, sign * amount * state.nF, state.pF, pSOL_current)
            return state._replace(nF=new_nF, nSOL=new_nSOL)
        
        elif action in [Action.MintXSOL, Action.BurnXSOL]:
            sign = 1 if action == Action.MintXSOL else -1
            new_nX, new_nSOL = mint_xSOL(state.nX, state.nSOL, sign * amount* state.nX, state.pX, pSOL_current)
            return state._replace(nX=new_nX, nSOL=new_nSOL)
        
        elif action == Action.StabilityPoolAdjustment:
            adjustment, changed = use_stability_pool(state.nF, self.fSOL_staked_per, amount, state.nX, state.pX, state.pF)
            new_nF = state.nF + adjustment
            return state._replace(nF=new_nF), changed
        
        elif action == Action.StabilityPool2Adjustment:
            adjustment_nF, adjustment_nX, changed = use_stability_pool_2(state.nSOL, state.nF, self.fSOL_staked_per_2, amount, state.nX, state.pX, state.pF, pSOL_current)
            new_nF = state.nF + adjustment_nF
            new_nX = state.nX + adjustment_nX
            return state._replace(nF=new_nF, nX=new_nX), changed   
                  
        elif action == Action.UpdateMarketPrices:
            new_pX = recalculate_pX(state.nSOL, pSOL_current, state.nF, state.pF, state.nX)
            return state._replace(pX=new_pX)
        
   

    def run_simulation(self, simulated_prices, stab_mod1, stab_mod2, stab_mod3):
        daily_data = []
        self.pSOL = simulated_prices[0]
        state = self.initialize_simulation(self.amount_SOL_initial,self.pSOL)
        stability_pool_non_zero_count = 0
        stability_pool_2_non_zero_count = 0
        xSOL_negative_price_count = 0
        

        for day, pSOL_current in enumerate(simulated_prices):
            state = self.handle_action(state, Action.UpdateMarketPrices, 0, pSOL_current)
            collateral_ratio = calculate_collateral_ratio(state.nSOL, pSOL_current, state.nF, state.pF)
            probabilities = get_action_probabilities(collateral_ratio, stab_mod2)
            amount_to_mint_per = get_mint_amount(collateral_ratio, self.config)

            actions = [
                (Action.MintFSOL if np.random.rand() < probabilities['fSOL_mint'] else Action.BurnFSOL, amount_to_mint_per['fSOL_mint_amount']),
                (Action.MintXSOL if np.random.rand() < probabilities['xSOL_mint'] else Action.BurnXSOL, amount_to_mint_per['xSOL_mint_amount'])
            ]

            for action, amount in actions:
                state = self.handle_action(state, action, amount, pSOL_current)

            state, stability_pool_changed = self.handle_action(state, Action.StabilityPoolAdjustment, stab_mod1)
            state, stability_pool_2_changed = self.handle_action(state, Action.StabilityPool2Adjustment, stab_mod3, pSOL_current)
            if stability_pool_changed:
                stability_pool_non_zero_count += 1

            if stability_pool_2_changed:
                stability_pool_2_non_zero_count+= 1

            day_data = {
                "day": day,
                "pSOL": pSOL_current,
                "nSOL": state.nSOL,
                "pF": state.pF,
                "nF": state.nF,
                "pX": state.pX,
                "nX": state.nX,
                "Marketcap fSOL": state.pF * state.nF,
                "Marketcap xSOL": state.pX * state.nX,
                "Collateralization ratio": collateral_ratio
            }
            daily_data.append(day_data)


            if state.pX * state.nX < 0:
                xSOL_negative_price_count += 1
            if state.pX < 0:
                break

        results_df = pd.DataFrame(daily_data)
        results_csv_path = './simulation_results.csv'
        results_df.to_csv(results_csv_path, index=False)

        return stability_pool_non_zero_count, xSOL_negative_price_count, collateral_ratio, stability_pool_2_non_zero_count
