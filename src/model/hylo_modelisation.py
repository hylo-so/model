from collections import namedtuple
import enum
import pandas as pd
import numpy as np
import configparser
from model.utils.simulation_utils import (mint_hyUSD, mint_xSOL, recalculate_pX, calculate_collateral_ratio, use_stability_pool_hyUSD, use_stability_pool_xSOL, update_hyUSD_in_stability_pool)
from model.utils.event_distributions import (get_action_probabilities, get_mint_amount)
from typing import Tuple, List, NamedTuple
from pandas import json_normalize



SimulationState = namedtuple('SimulationState', 'nSOL pF pX nF nX stabSOL_nF stabxSOL_nF')


class Action(enum.Enum):
    MintFSOL = 1
    BurnFSOL = 2
    MintXSOL = 3
    BurnXSOL = 4
    StabilityPoolSOL = 5
    StabilityPoolxSOL = 6
    UpdateMarketPrices = 7
    UpdatehyUSDInStabilityPool = 8

class StabilityPoolValues(NamedTuple):
    nSOL: float
    nF: float
    nX: float
    pX: float
    stab_nF: float

class UpdateStabilityPoolsResult(NamedTuple):
    state: 'SimulationState'
    stability_pool_hyUSD_xSOL_changed: bool
    stability_pool_hyUSD_SOL_changed: bool
    pre_UpdatehyUSDInStabilityPool_values: StabilityPoolValues
    post_UpdatehyUSDInStabilityPool_values: StabilityPoolValues
    collateral_ratio_post_stab_xSOL: float
    pre_StabilityPoolxSOL_values: StabilityPoolValues
    post_StabilityPoolxSOL_values: StabilityPoolValues
    pre_StabilityPoolSOL_values: StabilityPoolValues
    post_StabilityPoolSOL_values: StabilityPoolValues
    collateral_ratio_post_stab_SOL: float


class Simulation:
    def __init__(self, config_path: str = 'config.ini') -> None:
        config = configparser.ConfigParser()
        config.read(config_path)
        self.config = config
        self.amount_SOL_initial = config.getint('settings', 'amount_SOL_initial')
        self.hyUSD_staked_per = config.getfloat('settings', 'hyUSD_staked_per')
        self.min_recovery_per = config.getfloat('settings', 'min_recovery_per')
        self.max_recovery_per = config.getfloat('settings', 'max_recovery_per')       
        self.hyUSD_staked_per_2 = config.getfloat('settings', 'hyUSD_staked_per_2')
        self.min_recovery_per_2 = config.getfloat('settings', 'min_recovery_per_2')
        self.max_recovery_per_2 = config.getfloat('settings', 'max_recovery_per_2')    




    
    def initialize_simulation(self, nSOL: float, pSOL_initial: float) -> SimulationState:
        nF = (pSOL_initial * nSOL) / 2
        nX = nF
        stabSOL_nF = nF * self.hyUSD_staked_per
        stabxSOL_nF = nF * self.hyUSD_staked_per_2
        return SimulationState(nSOL=nSOL, pF=1, pX=1, nF=nF, nX=nX, stabSOL_nF=stabSOL_nF, stabxSOL_nF=stabxSOL_nF)

    def handle_action(
        self, 
        state: SimulationState, 
        action: Action, 
        amount: float, 
        pSOL_current: float = None,
        stab_mode_hyUSD_xSOL: float = None, 
        stab_mode_hyUSD_SOL: float = None       
    ) -> Tuple[SimulationState, bool]:
        if action in [Action.MintFSOL, Action.BurnFSOL]:
            sign = 1 if action == Action.MintFSOL else -1
            new_nF, new_nSOL = mint_hyUSD(state.nF, state.nSOL, sign * amount * state.nF, state.pF, pSOL_current)
            return state._replace(nF=new_nF, nSOL=new_nSOL), False
        
        elif action in [Action.MintXSOL, Action.BurnXSOL]:
            sign = 1 if action == Action.MintXSOL else -1
            new_nX, new_nSOL = mint_xSOL(state.nX, state.nSOL, sign * amount * state.nX, state.pX, pSOL_current)
            return state._replace(nX=new_nX, nSOL=new_nSOL), False
        
        elif action == Action.StabilityPoolSOL:
            adjustment, changed = use_stability_pool_hyUSD(state.nF, state.stabSOL_nF, amount, state.nX, state.pX, state.pF)
            new_nF, new_nSOL = mint_hyUSD(state.nF, state.nSOL, adjustment, state.pF, pSOL_current)
            new_stabSOL_nF = state.stabSOL_nF - (state.nF - new_nF)

            return state._replace(nF=new_nF, nSOL=new_nSOL, stabSOL_nF=new_stabSOL_nF), changed
        
        elif action == Action.StabilityPoolxSOL:
            adjustment_nF, adjustment_nX, changed = use_stability_pool_xSOL(state.nSOL, state.nF, state.stabxSOL_nF, amount, state.nX, state.pX, state.pF, pSOL_current)
            new_nF, new_nSOL_1 = mint_hyUSD(state.nF, state.nSOL, adjustment_nF, state.pF, pSOL_current)
            new_nX, new_nSOL_2 = mint_xSOL(state.nX, new_nSOL_1, adjustment_nX, state.pX, pSOL_current)
            new_stabxSOL_nF = state.stabxSOL_nF - (state.nF - new_nF)
            return state._replace(nF=new_nF, nX=new_nX, nSOL=new_nSOL_2, stabxSOL_nF=new_stabxSOL_nF), changed
        
        elif action == Action.UpdateMarketPrices:
            new_pX = recalculate_pX(state.nSOL, pSOL_current, state.nF, state.pF, state.nX)
            return state._replace(pX=new_pX), False
        
        elif action == Action.UpdatehyUSDInStabilityPool:
            if amount > stab_mode_hyUSD_SOL:
                new_stabSOL_nF = update_hyUSD_in_stability_pool(state.stabSOL_nF, state.nF, self.min_recovery_per, self.max_recovery_per, self.hyUSD_staked_per)
            else:
                new_stabSOL_nF = state.stabSOL_nF
            if amount > stab_mode_hyUSD_xSOL:
                new_stabxSOL_nF = update_hyUSD_in_stability_pool(state.stabxSOL_nF, state.nF, self.min_recovery_per_2, self.max_recovery_per_2, self.hyUSD_staked_per_2)
            else:
                new_stabxSOL_nF = state.stabxSOL_nF
            return state._replace(stabSOL_nF=new_stabSOL_nF, stabxSOL_nF=new_stabxSOL_nF), False
        
    
    def update_stability_pools(self, state, pSOL_current: float, stab_mode_hyUSD_xSOL: float, stab_mode_hyUSD_SOL: float, collateral_ratio: float) -> UpdateStabilityPoolsResult:
        pre_UpdatehyUSDInStabilityPool_values = StabilityPoolValues(
            nSOL=state.nSOL,
            nF=state.nF,
            nX=state.nX,
            pX=state.pX,
            stab_nF=state.stabSOL_nF
        )

        state, _ = self.handle_action(state, Action.UpdatehyUSDInStabilityPool, collateral_ratio, pSOL_current, stab_mode_hyUSD_xSOL, stab_mode_hyUSD_SOL)

        post_UpdatehyUSDInStabilityPool_values = StabilityPoolValues(
            nSOL=state.nSOL,
            nF=state.nF,
            nX=state.nX,
            pX=state.pX,
            stab_nF=state.stabSOL_nF
        )

        pre_StabilityPoolxSOL_values = StabilityPoolValues(
            nSOL=state.nSOL,
            nF=state.nF,
            nX=state.nX,
            pX=state.pX,
            stab_nF=state.stabxSOL_nF
        )

        if collateral_ratio < stab_mode_hyUSD_xSOL:
            state, stability_pool_hyUSD_xSOL_changed = self.handle_action(state, Action.StabilityPoolxSOL, stab_mode_hyUSD_xSOL, pSOL_current)
        else:
            stability_pool_hyUSD_xSOL_changed = False

        post_StabilityPoolxSOL_values = StabilityPoolValues(
            nSOL=state.nSOL,
            nF=state.nF,
            nX=state.nX,
            pX=state.pX,
            stab_nF=state.stabxSOL_nF
        )

        collateral_ratio_post_stab_xSOL = calculate_collateral_ratio(state.nSOL, pSOL_current, state.nF, state.pF)

        pre_StabilityPoolSOL_values = StabilityPoolValues(
            nSOL=state.nSOL,
            nF=state.nF,
            nX=state.nX,
            pX=state.pX,
            stab_nF=state.stabSOL_nF
        )

        if collateral_ratio_post_stab_xSOL < stab_mode_hyUSD_SOL:
            state, stability_pool_hyUSD_SOL_changed = self.handle_action(state, Action.StabilityPoolSOL, stab_mode_hyUSD_SOL, pSOL_current)
        else:
            stability_pool_hyUSD_SOL_changed = False

        post_StabilityPoolSOL_values = StabilityPoolValues(
            nSOL=state.nSOL,
            nF=state.nF,
            nX=state.nX,
            pX=state.pX,
            stab_nF=state.stabSOL_nF
        )

        collateral_ratio_post_stab_SOL = calculate_collateral_ratio(state.nSOL, pSOL_current, state.nF, state.pF)

        return UpdateStabilityPoolsResult(
            state=state,
            stability_pool_hyUSD_xSOL_changed = stability_pool_hyUSD_xSOL_changed,
            stability_pool_hyUSD_SOL_changed = stability_pool_hyUSD_SOL_changed,
            pre_UpdatehyUSDInStabilityPool_values = pre_UpdatehyUSDInStabilityPool_values,
            post_UpdatehyUSDInStabilityPool_values = post_UpdatehyUSDInStabilityPool_values,
            collateral_ratio_post_stab_xSOL = collateral_ratio_post_stab_xSOL,
            pre_StabilityPoolxSOL_values = pre_StabilityPoolxSOL_values,
            post_StabilityPoolxSOL_values = post_StabilityPoolxSOL_values,
            pre_StabilityPoolSOL_values = pre_StabilityPoolSOL_values,
            post_StabilityPoolSOL_values = post_StabilityPoolSOL_values,
            collateral_ratio_post_stab_SOL = collateral_ratio_post_stab_SOL
        )
    

    def run_simulation(
        self, 
        simulated_prices: List[float], 
        stab_mode_hyUSD_SOL: float, 
        stab_mode_fee_control: float, 
        stab_mode_hyUSD_xSOL: float,
        run_id: int,
        sub_run_id: float
    ) -> Tuple[int, int, float, int]:
        daily_data = []
        self.pSOL = simulated_prices[0]
        state = self.initialize_simulation(self.amount_SOL_initial, self.pSOL)
        stability_pool_hyUSD_SOL_non_zero_count = 0
        stability_pool_hyUSD_SOL_usage = 0
        stability_pool_hyUSD_xSOL_non_zero_count = 0
        stability_pool_hyUSD_xSOL_non_usage = 0
        xSOL_negative_price_count = 0

        for day, pSOL_current in enumerate(simulated_prices):
            state, _ = self.handle_action(state, Action.UpdateMarketPrices, 0, pSOL_current)
            collateral_ratio = calculate_collateral_ratio(state.nSOL, pSOL_current, state.nF, state.pF)
            probabilities = get_action_probabilities(collateral_ratio, stab_mode_fee_control)
            amount_to_mint_per = get_mint_amount(collateral_ratio, self.config)

            actions = [
                (Action.MintFSOL if np.random.rand() < probabilities['hyUSD_mint'] else Action.BurnFSOL, amount_to_mint_per['hyUSD_mint_amount']),
                (Action.MintXSOL if np.random.rand() < probabilities['xSOL_mint'] else Action.BurnXSOL, amount_to_mint_per['xSOL_mint_amount'])
            ]

            for action, amount in actions:
                state, _ = self.handle_action(state, action, amount, pSOL_current)

            
            result = self.update_stability_pools(
                state, pSOL_current, stab_mode_hyUSD_xSOL, stab_mode_hyUSD_SOL, collateral_ratio
            )

            state = result.state

            stability_pool_hyUSD_xSOL_usage_nF_redeemed = result.pre_StabilityPoolxSOL_values.nF - result.post_StabilityPoolxSOL_values.nF
            stability_pool_hyUSD_SOL_usage_nF_redeemed = result.pre_StabilityPoolSOL_values.nF - result.post_StabilityPoolSOL_values.nF

            if result.stability_pool_hyUSD_xSOL_changed:
                stability_pool_hyUSD_xSOL_non_zero_count += 1
                stability_pool_hyUSD_xSOL_non_usage += stability_pool_hyUSD_xSOL_usage_nF_redeemed

            if result.stability_pool_hyUSD_SOL_changed:
                stability_pool_hyUSD_SOL_non_zero_count += 1
                stability_pool_hyUSD_SOL_usage += stability_pool_hyUSD_SOL_usage_nF_redeemed

            day_data = {
            "day": day,
            "pSOL": pSOL_current,
            "pre_nSOL_SOL": result.pre_StabilityPoolSOL_values.nSOL,
            "pre_nSOL_xSOL": result.pre_StabilityPoolxSOL_values.nSOL,
            "nSOL": state.nSOL,
            "pre_nF_xSOL": result.pre_StabilityPoolxSOL_values.nF,
            "pre_nF_SOL": result.pre_StabilityPoolSOL_values.nF,
            "pF": state.pF,
            "nF": state.nF,
            "pre_pX_xSOL": result.pre_StabilityPoolxSOL_values.pX,
            "pre_pX_SOL": result.pre_StabilityPoolSOL_values.pX,
            "pX": state.pX,
            "pre_nX_xSOL": result.pre_StabilityPoolxSOL_values.nX,
            "pre_nX_SOL": result.pre_StabilityPoolSOL_values.nX,
            "nX": state.nX,
            "marketcap_hyUSD": state.pF * state.nF,
            "marketcap_xSOL": state.pX * state.nX,
            "xSOL_leverage" : state.nSOL/ (state.pX * state.nX / pSOL_current),
            "collateralization_ratio_initial": collateral_ratio,
            "collateralization_ratio_post_stab_xSOL": result.collateral_ratio_post_stab_xSOL,
            "collateralization_ratio_post_stab_SOL": result.collateral_ratio_post_stab_SOL,
            "stab_xSOL_nSOL_removed": result.pre_StabilityPoolxSOL_values.nSOL - result.post_StabilityPoolxSOL_values.nSOL,
            "stab_xSOL_nF_burned": stability_pool_hyUSD_xSOL_usage_nF_redeemed,
            "stab_xSOL_nX_minted": result.post_StabilityPoolxSOL_values.nX - result.pre_StabilityPoolxSOL_values.nX,
            "stab_SOL_nSOL_moved": result.pre_StabilityPoolSOL_values.nSOL - result.post_StabilityPoolSOL_values.nSOL,
            "stab_SOL_nF_burned": stability_pool_hyUSD_SOL_usage_nF_redeemed,
            "stab_SOL_nX_minted": result.post_StabilityPoolSOL_values.nX - result.pre_StabilityPoolSOL_values.nX,
            "pre_stabSOL_nF": result.pre_UpdatehyUSDInStabilityPool_values.stab_nF,
            "post_stabSOL_nF": result.post_UpdatehyUSDInStabilityPool_values.stab_nF,
            "stabSOL_nF": state.stabSOL_nF,
            "pre_stabxSOL_nF": result.pre_UpdatehyUSDInStabilityPool_values.stab_nF,
            "post_stabxSOL_nF": result.post_UpdatehyUSDInStabilityPool_values.stab_nF,
            "stabxSOL_nF": state.stabxSOL_nF,
        }

            daily_data.append(day_data)

            if collateral_ratio < 1:
                xSOL_negative_price_count += 1
                break

        results_df = pd.DataFrame(daily_data)
        results_csv_path = f'./output/run_{run_id}.{sub_run_id}-SOL_{stab_mode_hyUSD_SOL}-FEE_{stab_mode_fee_control}-xSOL_{stab_mode_hyUSD_xSOL}.csv'
        results_df.to_csv(results_csv_path, index=False)

        return stability_pool_hyUSD_SOL_non_zero_count, xSOL_negative_price_count, collateral_ratio, stability_pool_hyUSD_xSOL_non_zero_count, stability_pool_hyUSD_xSOL_non_usage, stability_pool_hyUSD_SOL_usage
