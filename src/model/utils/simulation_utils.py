import numpy as np
from typing import NamedTuple

class MintResult(NamedTuple):
    updated_n: float
    updated_nSOL: float

class StabilityPoolxSOLResult(NamedTuple):
    hyUSD_to_burn: float
    xSOL_to_mint: float
    changed: bool


class StabilityPoolFSOLResult(NamedTuple):
    hyUSD_to_burn: float
    changed: bool


class AdjustFSOLResult(NamedTuple):
    hyUSD_burned: float
    xSOL_SOL_mcap: float
    SOL_moved: float


def adjust_SOL_reserve(
    nSOL: float, 
    amount_in_dollars: float, 
    pSOL_current: float
) -> float:
    """
    Adjusts the SOL reserve based on the amount in dollars and the current price of SOL.

    Args:
        nSOL (float): The current amount of SOL.
        amount_in_dollars (float): The amount in dollars to convert to SOL.
        pSOL_current (float): The current price of SOL.

    Returns:
        float: The updated amount of SOL.
    """
    SOL_change = amount_in_dollars / pSOL_current
    return nSOL + SOL_change

def mint_hyUSD(
    nF: float, 
    nSOL: float, 
    amount: float, 
    pF: float, 
    pSOL_current: float
) -> MintResult:
    """
    Mints hyUSD and adjusts the SOL reserve accordingly.

    Args:
        nF (float): The current amount of hyUSD.
        nSOL (float): The current amount of SOL.
        amount (float): The amount of hyUSD to mint.
        pF (float): The price of hyUSD.
        pSOL_current (float): The current price of SOL.

    Returns:
        MintResult: A named tuple containing:
            updated_n (float): The updated amount of hyUSD.
            updated_nSOL (float): The updated amount of SOL.
    """
    nF += amount
    amount_in_dollars = amount * pF
    nSOL = adjust_SOL_reserve(nSOL, amount_in_dollars, pSOL_current)
    return MintResult(nF, nSOL)

def mint_xSOL(
    nX: float, 
    nSOL: float, 
    amount: float, 
    pX: float, 
    pSOL_current: float
) -> MintResult:
    """
    Mints xSOL and adjusts the SOL reserve accordingly.

    Args:
        nX (float): The current amount of xSOL.
        nSOL (float): The current amount of SOL.
        amount (float): The amount of xSOL to mint.
        pX (float): The price of xSOL.
        pSOL_current (float): The current price of SOL.

    Returns:
        MintResult: A named tuple containing:
            updated_n (float): The updated amount of xSOL.
            updated_nSOL (float): The updated amount of SOL.
    """
    nX += amount
    amount_in_dollars = amount * pX
    nSOL = adjust_SOL_reserve(nSOL, amount_in_dollars, pSOL_current)
    return MintResult(nX, nSOL)

def recalculate_pX(
    nSOL: float, 
    pSOL_current: float, 
    nF: float, 
    pF: float, 
    nX: float
) -> float:
    """
    Recalculates the price of xSOL based on the new SOL value.

    Args:
        nSOL (float): The current amount of SOL.
        pSOL_current (float): The current price of SOL.
        nF (float): The current amount of hyUSD.
        pF (float): The price of hyUSD.
        nX (float): The current amount of xSOL.

    Returns:
        float: The recalculated price of xSOL.
    """
    total_value_current = nSOL * pSOL_current
    pX = (total_value_current - (nF * pF)) / nX
    return pX

def calculate_collateral_ratio(
    nSOL: float, 
    pSOL: float, 
    nF: float, 
    pF: float
) -> float:
    """
    Calculates the collateralization ratio of hyUSD.

    Args:
        nSOL (float): The current amount of SOL.
        pSOL (float): The price of SOL.
        nF (float): The current amount of hyUSD.
        pF (float): The price of hyUSD.

    Returns:
        float: The collateralization ratio of hyUSD.
    """
    total_SOL_value = nSOL * pSOL
    market_cap_hyUSD = nF * pF
    collateralization_ratio_hyUSD = total_SOL_value / market_cap_hyUSD
    return collateralization_ratio_hyUSD

def adjust_hyUSD_to_target_CR(
    nF: float, 
    nX: float, 
    pX: float, 
    pF: float, 
    stab_mode1: float
) -> float:
    """
    Adjusts hyUSD to reach the target collateral ratio.

    Args:
        nF (float): The current amount of hyUSD.
        nX (float): The current amount of xSOL.
        pX (float): The price of xSOL.
        pF (float): The price of hyUSD.
        stab_mode1 (float): The hyUSD stability mode collateral ratio activation threshold.

    Returns:
        float: The adjustment required for hyUSD.
    """
    if abs(stab_mode1 - 1) < 1e-10:  # Using small epsilon instead of exact 0
        return 0
    nF_required = (nX * pX) / (pF * (stab_mode1 - 1))
    hyUSD_adjustment = nF_required - nF
    return hyUSD_adjustment if hyUSD_adjustment <= 0 else 0

def update_hyUSD_in_stability_pool(
    stab_nF: float, 
    nF: float, 
    min_recovery_per: float, 
    max_recovery_per: float, 
    hyUSD_max_staked_per: float
) -> float:
    """
    Updates the amount of hyUSD in the stability pool.

    Args:
        stab_nF (float): The current amount of hyUSD in the stability pool.
        nF (float): The current amount of hyUSD.
        min_recovery_per (float): The minimum recovery percentage.
        max_recovery_per (float): The maximum recovery percentage.
        hyUSD_max_staked_per (float): The maximum percentage of hyUSD that can be staked.

    Returns:
        float: The updated amount of hyUSD in the stability pool.
    """
    recovery_amount = nF * np.random.uniform(min_recovery_per, max_recovery_per)
    stab_nF += recovery_amount
    cap_amount = nF * hyUSD_max_staked_per
    if stab_nF > cap_amount:
        stab_nF = cap_amount
    return stab_nF

def use_stability_pool_hyUSD(
    nF: float, 
    stab_nF: float, 
    stab_mode1: float, 
    nX: float, 
    pX: float, 
    pF: float
) -> StabilityPoolFSOLResult:
    """
    Uses hyUSD from the stability pool to adjust to the target collateral ratio.

    Args:
        nF (float): The current amount of hyUSD.
        stab_nF (float): The amount of hyUSD in the stability pool.
        stab_mode1 (float): The hyUSD stability mode collateral ratio activation threshold.
        nX (float): The current amount of xSOL.
        pX (float): The price of xSOL.
        pF (float): The price of hyUSD.

    Returns:
        StabilityPoolFSOLResult: A named tuple containing:
            hyUSD_to_burn (float): The amount of hyUSD to burn.
            changed (bool): Whether any changes were made.
    """
    hyUSD_adjustment = adjust_hyUSD_to_target_CR(nF, nX, pX, pF, stab_mode1)
    if hyUSD_adjustment < 0:
        max_hyUSD_to_burn = stab_nF
        hyUSD_to_burn = -min(-hyUSD_adjustment, max_hyUSD_to_burn)
        if hyUSD_to_burn != 0:
            return StabilityPoolFSOLResult(hyUSD_to_burn, True)
    return StabilityPoolFSOLResult(0, False)


def adjust_hyUSD_to_target_CR_xSOL(
    nF: float, 
    nX: float, 
    nSOL: float, 
    pX: float, 
    pF: float, 
    pSOL: float, 
    stab_mode2: float
) -> AdjustFSOLResult:
    """
    Adjusts hyUSD to target collateral ratio using xSOL.

    Args:
        nF (float): The current amount of hyUSD.
        nX (float): The current amount of xSOL.
        nSOL (float): The current amount of SOL.
        pX (float): The price of xSOL.
        pF (float): The price of hyUSD.
        pSOL (float): The price of SOL.
        stab_mode2 (float): The xSOL stability mode collateral ratio activation threshold.

    Returns:
        AdjustFSOLResult: A named tuple containing:
            hyUSD_burned (float): The amount of hyUSD to burn.
            xSOL_SOL_mcap (float): The xSOL market cap in SOL.
            SOL_moved (float): The amount of SOL moved.
    """
    hyUSD_SOL_mcap = nF * pF / pSOL  # Total hyUSD market cap in SOL
    xSOL_SOL_mcap = nSOL - hyUSD_SOL_mcap
    target_SOL = nSOL / stab_mode2
    SOL_moved = hyUSD_SOL_mcap - target_SOL
    if SOL_moved > 0:
        hyUSD_burned = SOL_moved / (hyUSD_SOL_mcap / nF)  # Amount of hyUSD to burn
        return AdjustFSOLResult(hyUSD_burned, xSOL_SOL_mcap, SOL_moved)
    return AdjustFSOLResult(0, 0, 0)

def use_stability_pool_xSOL(
    nSOL: float, 
    nF: float, 
    stab2_nF: float, 
    stab_mode2: float, 
    nX: float, 
    pX: float, 
    pF: float, 
    pSOL_current: float
) -> StabilityPoolxSOLResult:
    """
    Adjusts hyUSD to target collateral ratio using xSOL and returns the results.

    Args:
        nSOL (float): The amount of SOL.
        nF (float): The amount of hyUSD.
        stab2_nF (float): The amount of nF in xSOL stability pool.
        stab_mode2 (float): The xSOL stability mode collateral ratio activation threshold.
        nX (float): The amount of xSOL.
        pX (float): The price of xSOL.
        pF (float): The price of hyUSD.
        pSOL_current (float): The current price of SOL.

    Returns:
        StabilityPoolxSOLResult: A named tuple containing:
            hyUSD_to_burn (float): The amount of hyUSD to burn.
            xSOL_to_mint (float): The amount of xSOL to mint.
            changed (bool): Whether any changes were made.
    """
    hyUSD_burned, xSOL_SOL_mcap, SOL_moved = adjust_hyUSD_to_target_CR_xSOL(nF, nX, nSOL, pX, pF, pSOL_current, stab_mode2)
    if hyUSD_burned > 0:
        max_hyUSD_to_burn = stab2_nF
        hyUSD_to_burn = min(hyUSD_burned, max_hyUSD_to_burn)
        SOL_moved_2 = hyUSD_to_burn * (pF / pSOL_current)
        xSOL_to_mint = SOL_moved_2 / (xSOL_SOL_mcap / nX) 
        if hyUSD_to_burn > 0:
            return StabilityPoolxSOLResult(-hyUSD_to_burn, xSOL_to_mint, True)
    return StabilityPoolxSOLResult(0, 0, False)
