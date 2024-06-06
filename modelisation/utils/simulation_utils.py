import numpy as np


def adjust_SOL_reserve(
    nSOL: float, 
    amount_in_dollars: float, 
    pSOL_current: float
) -> float:
    SOL_change = amount_in_dollars / pSOL_current
    return nSOL + SOL_change

def mint_fSOL(
    nF: float, 
    nSOL: float, 
    amount: float, 
    pF: float, 
    pSOL_current: float
) -> tuple[float, float]:
    nF += amount
    amount_in_dollars = amount * pF
    nSOL = adjust_SOL_reserve(nSOL, amount_in_dollars, pSOL_current)
    return nF, nSOL

def mint_xSOL(
    nX: float, 
    nSOL: float, 
    amount: float, 
    pX: float, 
    pSOL_current: float
) -> tuple[float, float]:
    nX += amount
    amount_in_dollars = amount * pX
    nSOL = adjust_SOL_reserve(nSOL, amount_in_dollars, pSOL_current)
    return nX, nSOL

def recalculate_pX(
    nSOL: float, 
    pSOL_current: float, 
    nF: float, 
    pF: float, 
    nX: float
) -> float:
    total_value_current = nSOL * pSOL_current
    pX = (total_value_current - (nF * pF)) / nX
    return pX

def calculate_collateral_ratio(
    nSOL: float, 
    pSOL: float, 
    nF: float, 
    pF: float
) -> float:
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
    recovery_amount = nF * np.random.uniform(min_recovery_per, max_recovery_per)
    stab_nF += recovery_amount
    cap_amount = nF * fSOL_max_staked_per
    if stab_nF > cap_amount:
        stab_nF = cap_amount
    return stab_nF


def use_stability_pool(
    nF: float, 
    stab_nF: float, 
    stab_mod1: float, 
    nX: float, 
    pX: float, 
    pF: float
) -> tuple[float, bool]:
    fSOL_adjustment = adjust_fSOL_to_target_CR(nF, nX, pX, pF, stab_mod1)
    if fSOL_adjustment < 0:
        max_fSOL_to_burn = stab_nF
        fSOL_to_burn = -min(-fSOL_adjustment, max_fSOL_to_burn)
        if fSOL_to_burn != 0:
            return fSOL_to_burn, True
    return 0, False

def adjust_fSOL_to_target_CR_2(
    nF: float, 
    nX: float, 
    nSOL: float, 
    pX: float, 
    pF: float, 
    pSOL: float, 
    stab_mod2: float
) -> tuple[float, float, float]:
    fSOL_SOL_mcap = nF * pF / pSOL  # Total fSOL market cap in SOL
    xSOL_SOL_mcap = nSOL - fSOL_SOL_mcap
    target_SOL = nSOL / stab_mod2
    SOL_moved = fSOL_SOL_mcap - target_SOL
    if SOL_moved > 0:
        fSOL_burned = SOL_moved / (fSOL_SOL_mcap / nF)  # Amount of fSOL to burn
        return fSOL_burned, xSOL_SOL_mcap, SOL_moved
    return 0, 0, 0

def use_stability_pool_2(
    nSOL: float, 
    nF: float, 
    stab2_nF: float, 
    stab_mod2: float, 
    nX: float, 
    pX: float, 
    pF: float, 
    pSOL_current: float
) -> tuple[float, float, bool]:
    fSOL_burned, xSOL_SOL_mcap, SOL_moved = adjust_fSOL_to_target_CR_2(nF, nX, nSOL, pX, pF, pSOL_current, stab_mod2)
    if fSOL_burned > 0:
        max_fSOL_to_burn = stab2_nF
        fSOL_to_burn = min(fSOL_burned, max_fSOL_to_burn)
        xSOL_to_mint = SOL_moved / (xSOL_SOL_mcap / nX) 
        if fSOL_to_burn != 0:
            return -fSOL_to_burn, xSOL_to_mint, True
    return 0, 0, False

