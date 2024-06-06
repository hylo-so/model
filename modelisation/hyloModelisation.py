from collections import namedtuple
import enum
import pandas as pd
import numpy as np
import configparser
from utils.simulation_utils import (mint_fSOL, mint_xSOL, recalculate_pX, calculate_collateral_ratio, use_stability_pool, use_stability_pool_2)
from utils.event_distributions import (get_action_probabilities, get_mint_amount)
from typing import Tuple, List

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
    def __init__(self, config_path: str = 'config.ini') -> None:
        config = configparser.ConfigParser()
        config.read(config_path)
        self.config = config
        self.amount_SOL_initial = config.getint('settings', 'amount_SOL_initial')
        self.fSOL_staked_per = config.getfloat('settings', 'fSOL_staked_per')
        self.fSOL_staked_per_2 = config.getfloat('settings', 'fSOL_staked_per_2')
    
    def initialize_simulation(self, nSOL: float, pSOL_initial: float) -> SimulationState:
        nF = (pSOL_initial * nSOL) / 2
        nX = nF
        return SimulationState(nSOL=nSOL, pF=1, pX=1, nF=nF, nX=nX)

    def handle_action(
        self, 
        state: SimulationState, 
        action: Action, 
        amount: float, 
        pSOL_current: float = None
    ) -> Tuple[SimulationState, bool]:
        if action in [Action.MintFSOL, Action.BurnFSOL]:
            sign = 1 if action == Action.MintFSOL else -1
            new_nF, new_nSOL = mint_fSOL(state.nF, state.nSOL, sign * amount * state.nF, state.pF, pSOL_current)
            return state._replace(nF=new_nF, nSOL=new_nSOL), False
        
        elif action in [Action.MintXSOL, Action.BurnXSOL]:
            sign = 1 if action == Action.MintXSOL else -1
            new_nX, new_nSOL = mint_xSOL(state.nX, state.nSOL, sign * amount * state.nX, state.pX, pSOL_current)
            return state._replace(nX=new_nX, nSOL=new_nSOL), False
        
        elif action == Action.StabilityPoolAdjustment:
            adjustment, changed = use_stability_pool(state.nF, self.fSOL_staked_per, amount, state.nX, state.pX, state.pF)
            new_nF, new_nSOL = mint_fSOL(state.nF, state.nSOL, adjustment, state.pF, pSOL_current)
            return state._replace(nF=new_nF, nSOL=new_nSOL), changed
        
        elif action == Action.StabilityPool2Adjustment:
            adjustment_nF, adjustment_nX, changed = use_stability_pool_2(state.nSOL, state.nF, self.fSOL_staked_per_2, amount, state.nX, state.pX, state.pF, pSOL_current)
            new_nF, new_nSOL_1 = mint_fSOL(state.nF, state.nSOL, adjustment_nF, state.pF, pSOL_current)
            new_nX, new_nSOL_2 = mint_xSOL(state.nX, new_nSOL_1, adjustment_nX, state.pX, pSOL_current)
            return state._replace(nF=new_nF, nX=new_nX, nSOL=new_nSOL_2), changed
        
        elif action == Action.UpdateMarketPrices:
            new_pX = recalculate_pX(state.nSOL, pSOL_current, state.nF, state.pF, state.nX)
            return state._replace(pX=new_pX), False

    def run_simulation(
        self, 
        simulated_prices: List[float], 
        stab_mod_fSOL_SOL: float, 
        stab_mod_fee_control: float, 
        stab_mod_fSOL_xSOL: float
    ) -> Tuple[int, int, float, int]:
        daily_data = []
        self.pSOL = simulated_prices[0]
        state = self.initialize_simulation(self.amount_SOL_initial, self.pSOL)
        stability_pool_fSOL_SOL_non_zero_count = 0
        stability_pool_fSOL_xSOL_non_zero_count = 0
        xSOL_negative_price_count = 0
        print('xsol', stab_mod_fSOL_xSOL, 'sol', stab_mod_fSOL_SOL)

        for day, pSOL_current in enumerate(simulated_prices):
            state, _ = self.handle_action(state, Action.UpdateMarketPrices, 0, pSOL_current)
            collateral_ratio = calculate_collateral_ratio(state.nSOL, pSOL_current, state.nF, state.pF)
            probabilities = get_action_probabilities(collateral_ratio, stab_mod_fee_control)
            amount_to_mint_per = get_mint_amount(collateral_ratio, self.config)

            actions = [
                (Action.MintFSOL if np.random.rand() < probabilities['fSOL_mint'] else Action.BurnFSOL, amount_to_mint_per['fSOL_mint_amount']),
                (Action.MintXSOL if np.random.rand() < probabilities['xSOL_mint'] else Action.BurnXSOL, amount_to_mint_per['xSOL_mint_amount'])
            ]

            for action, amount in actions:
                state, _ = self.handle_action(state, action, amount, pSOL_current)

            #Used for tracking between each step, pre usage of stability pool fSOL_xSOL 
            pre_nSOL = state.nSOL
            pre_nF = state.nF
            pre_nX = state.nX
            pre_pX = state.pX

            state, stability_pool_fSOL_xSOL_changed = self.handle_action(state, Action.StabilityPool2Adjustment, stab_mod_fSOL_xSOL, pSOL_current)

            #Used for tracking between each step, post usage of stability pool fSOL_xSOL
            pre_nSOL1 = state.nSOL
            pre_nF1 = state.nF
            pre_nX1 = state.nX
            pre_pX1 = state.pX

            collateral_ratio_post_1 = calculate_collateral_ratio(state.nSOL, pSOL_current, state.nF, state.pF)
            
            state, stability_pool_changed = self.handle_action(state, Action.StabilityPoolAdjustment, stab_mod_fSOL_SOL, pSOL_current)

            #Used for tracking between each step, post usage of stability pool fSOL_SOL
            pre_nSOL2 = state.nSOL
            pre_nF2 = state.nF
            pre_nX2 = state.nX
            pre_pX2 = state.pX
            
            collateral_ratio_post_2 = calculate_collateral_ratio(state.nSOL, pSOL_current, state.nF, state.pF)

            if stability_pool_changed:
                stability_pool_fSOL_SOL_non_zero_count += 1

            if stability_pool_fSOL_xSOL_changed:
                stability_pool_fSOL_xSOL_non_zero_count += 1

            day_data = {
                "day": day,
                "pSOL": pSOL_current,
                "pre_nSOL1": pre_nSOL1,
                "pre_nSOL": pre_nSOL,
                "nSOL": state.nSOL,
                "pre_nF": pre_nF,
                "pre_nF1": pre_nF1,
                "pF": state.pF,
                "nF": state.nF,
                "pre_pX": pre_pX,
                "pre_pX1": pre_pX1,
                "pX": state.pX,
                "pre_nX": pre_nX,
                "pre_nX1": pre_nX1,
                "nX": state.nX,
                "Marketcap fSOL": state.pF * state.nF,
                "Marketcap xSOL": state.pX * state.nX,
                "Collateralization ratio": collateral_ratio,
                "Collateralization ratio Post Stab1": collateral_ratio_post_1,
                "Collateralization ratio Post Stab2": collateral_ratio_post_2,
                "Stab1 nSOL removed": pre_nSOL - pre_nSOL1,
                "Stab1 nF burned": pre_nF - pre_nF1,
                "Stab1 nX minted": pre_nX1 - pre_nX,
                "Stab2 nSOL moved": pre_nSOL1 - pre_nSOL2,
                "Stab2 nF burned": pre_nF1 - pre_nF2,
                "Stab2 nX minted": pre_nX2 - pre_nX1 
            }
            daily_data.append(day_data)

            if collateral_ratio < 1:
                xSOL_negative_price_count += 1
                break

        results_df = pd.DataFrame(daily_data)
        results_csv_path = './simulation_results.csv'
        results_df.to_csv(results_csv_path, index=False)

        return stability_pool_fSOL_SOL_non_zero_count, xSOL_negative_price_count, collateral_ratio, stability_pool_fSOL_xSOL_non_zero_count
