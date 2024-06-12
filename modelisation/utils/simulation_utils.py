import numpy as np
from typing import NamedTuple

class MintResult(NamedTuple):
    updated_n: float
    updated_nSOL: float

class StabilityPoolxSOLResult(NamedTuple):
    fSOL_to_burn: float
    xSOL_to_mint: float
    changed: bool


class StabilityPoolFSOLResult(NamedTuple):
    fSOL_to_burn: float
    changed: bool


class AdjustFSOLResult(NamedTuple):
    fSOL_burned: float
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

def mint_fSOL(
    nF: float, 
    nSOL: float, 
    amount: float, 
    pF: float, 
    pSOL_current: float
) -> MintResult:
    """
    Mints fSOL and adjusts the SOL reserve accordingly.

    Args:
        nF (float): The current amount of fSOL.
        nSOL (float): The current amount of SOL.
        amount (float): The amount of fSOL to mint.
        pF (float): The price of fSOL.
        pSOL_current (float): The current price of SOL.

    Returns:
        MintResult: A named tuple containing:
            updated_n (float): The updated amount of fSOL.
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
        nF (float): The current amount of fSOL.
        pF (float): The price of fSOL.
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
    Calculates the collateralization ratio of fSOL.

    Args:
        nSOL (float): The current amount of SOL.
        pSOL (float): The price of SOL.
        nF (float): The current amount of fSOL.
        pF (float): The price of fSOL.

    Returns:
        float: The collateralization ratio of fSOL.
    """
    total_SOL_value = nSOL * pSOL
    market_cap_fSOL = nF * pF
    collateralization_ratio_fSOL = total_SOL_value / market_cap_fSOL
    return collateralization_ratio_fSOL

def adjust_fSOL_to_target_CR(
    nF: float, 
    nX: float, 
    pX: float, 
    pF: float, 
    stab_mod1: float
) -> float:
    """
    Adjusts fSOL to reach the target collateral ratio.

    Args:
        nF (float): The current amount of fSOL.
        nX (float): The current amount of xSOL.
        pX (float): The price of xSOL.
        pF (float): The price of fSOL.
        stab_mod1 (float): The xSOL stability mod collateral ratio activation threshold.

    Returns:
        float: The adjustment required for fSOL.
    """
    nF_required = (nX * pX) / (pF * (stab_mod1 - 1))
    fSOL_adjustment = nF_required - nF
    return fSOL_adjustment if fSOL_adjustment <= 0 else 0

def update_fSOL_in_stability_pool(
    stab_nF: float, 
    nF: float, 
    min_recovery_per: float, 
    max_recovery_per: float, 
    fSOL_max_staked_per: float
) -> float:
    """
    Updates the amount of fSOL in the stability pool.

    Args:
        stab_nF (float): The current amount of fSOL in the stability pool.
        nF (float): The current amount of fSOL.
        min_recovery_per (float): The minimum recovery percentage.
        max_recovery_per (float): The maximum recovery percentage.
        fSOL_max_staked_per (float): The maximum percentage of fSOL that can be staked.

    Returns:
        float: The updated amount of fSOL in the stability pool.
    """
    recovery_amount = nF * np.random.uniform(min_recovery_per, max_recovery_per)
    stab_nF += recovery_amount
    cap_amount = nF * fSOL_max_staked_per
    if stab_nF > cap_amount:
        stab_nF = cap_amount
    return stab_nF

def use_stability_pool_fSOL(
    nF: float, 
    stab_nF: float, 
    stab_mod1: float, 
    nX: float, 
    pX: float, 
    pF: float
) -> StabilityPoolFSOLResult:
    """
    Uses fSOL from the stability pool to adjust to the target collateral ratio.

    Args:
        nF (float): The current amount of fSOL.
        stab_nF (float): The amount of fSOL in the stability pool.
        stab_mod1 (float): The fSOL stability mod collateral ratio activation threshold.
        nX (float): The current amount of xSOL.
        pX (float): The price of xSOL.
        pF (float): The price of fSOL.

    Returns:
        StabilityPoolFSOLResult: A named tuple containing:
            fSOL_to_burn (float): The amount of fSOL to burn.
            changed (bool): Whether any changes were made.
    """
    fSOL_adjustment = adjust_fSOL_to_target_CR(nF, nX, pX, pF, stab_mod1)
    if fSOL_adjustment < 0:
        max_fSOL_to_burn = stab_nF
        fSOL_to_burn = -min(-fSOL_adjustment, max_fSOL_to_burn)
        if fSOL_to_burn != 0:
            return StabilityPoolFSOLResult(fSOL_to_burn, True)
    return StabilityPoolFSOLResult(0, False)


def adjust_fSOL_to_target_CR_xSOL(
    nF: float, 
    nX: float, 
    nSOL: float, 
    pX: float, 
    pF: float, 
    pSOL: float, 
    stab_mod2: float
) -> AdjustFSOLResult:
    """
    Adjusts fSOL to target collateral ratio using xSOL.

    Args:
        nF (float): The current amount of fSOL.
        nX (float): The current amount of xSOL.
        nSOL (float): The current amount of SOL.
        pX (float): The price of xSOL.
        pF (float): The price of fSOL.
        pSOL (float): The price of SOL.
        stab_mod2 (float): The xSOL stability mod collateral ratio activation threshold.

    Returns:
        AdjustFSOLResult: A named tuple containing:
            fSOL_burned (float): The amount of fSOL to burn.
            xSOL_SOL_mcap (float): The xSOL market cap in SOL.
            SOL_moved (float): The amount of SOL moved.
    """
    fSOL_SOL_mcap = nF * pF / pSOL  # Total fSOL market cap in SOL
    xSOL_SOL_mcap = nSOL - fSOL_SOL_mcap
    target_SOL = nSOL / stab_mod2
    SOL_moved = fSOL_SOL_mcap - target_SOL
    if SOL_moved > 0:
        fSOL_burned = SOL_moved / (fSOL_SOL_mcap / nF)  # Amount of fSOL to burn
        return AdjustFSOLResult(fSOL_burned, xSOL_SOL_mcap, SOL_moved)
    return AdjustFSOLResult(0, 0, 0)

def use_stability_pool_xSOL(
    nSOL: float, 
    nF: float, 
    stab2_nF: float, 
    stab_mod2: float, 
    nX: float, 
    pX: float, 
    pF: float, 
    pSOL_current: float
) -> StabilityPoolxSOLResult:
    """
    Adjusts fSOL to target collateral ratio using xSOL and returns the results.

    Args:
        nSOL (float): The amount of SOL.
        nF (float): The amount of fSOL.
        stab2_nF (float): The amount of nF in xSOL stability pool.
        stab_mod2 (float): The xSOL stability mod collateral ratio activation threshold.
        nX (float): The amount of xSOL.
        pX (float): The price of xSOL.
        pF (float): The price of fSOL.
        pSOL_current (float): The current price of SOL.

    Returns:
        StabilityPoolxSOLResult: A named tuple containing:
            fSOL_to_burn (float): The amount of fSOL to burn.
            xSOL_to_mint (float): The amount of xSOL to mint.
            changed (bool): Whether any changes were made.
    """
    fSOL_burned, xSOL_SOL_mcap, SOL_moved = adjust_fSOL_to_target_CR_xSOL(nF, nX, nSOL, pX, pF, pSOL_current, stab_mod2)
    if fSOL_burned > 0:
        max_fSOL_to_burn = stab2_nF
        fSOL_to_burn = min(fSOL_burned, max_fSOL_to_burn)
        SOL_moved_2 = fSOL_to_burn * (pF / pSOL_current)
        xSOL_to_mint = SOL_moved_2 / (xSOL_SOL_mcap / nX) 
        if fSOL_to_burn > 0:
            return StabilityPoolxSOLResult(-fSOL_to_burn, xSOL_to_mint, True)
    return StabilityPoolxSOLResult(0, 0, False)
