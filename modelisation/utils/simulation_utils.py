def adjust_SOL_reserve(nSOL, amount_in_dollars, pSOL_current):
    SOL_change = amount_in_dollars / pSOL_current
    return nSOL + SOL_change

def mint_fSOL(nF, nSOL, amount, pF, pSOL_current):
    nF += amount
    amount_in_dollars = amount * pF
    nSOL = adjust_SOL_reserve(nSOL, amount_in_dollars, pSOL_current)
    return nF, nSOL

def mint_xSOL(nX, nSOL, amount, pX, pSOL_current):
    nX += amount
    amount_in_dollars = amount * pX
    nSOL = adjust_SOL_reserve(nSOL, amount_in_dollars, pSOL_current)
    return nX, nSOL

def recalculate_pX(nSOL, pSOL_current, nF, pF, nX):
    total_value_current = nSOL * pSOL_current
    pX = (total_value_current - (nF * pF)) / nX
    return pX

def calculate_collateral_ratio(nSOL, pSOL, nF, pF):
    total_SOL_value = nSOL * pSOL
    market_cap_fSOL = nF * pF
    collateralization_ratio_fSOL = total_SOL_value / market_cap_fSOL
    return collateralization_ratio_fSOL

def adjust_fSOL_to_target_CR(nF, nX, pX, pF, stab_mod1):
    nF_required = (nX * pX) / (pF * (stab_mod1 - 1))
    fSOL_adjustment = nF_required - nF
    return fSOL_adjustment if fSOL_adjustment <= 0 else 0

def use_stability_pool(nF, fSOL_staked_per, stab_mod1, nX, pX, pF):
    fSOL_adjustment = adjust_fSOL_to_target_CR(nF, nX, pX, pF, stab_mod1)
    if fSOL_adjustment < 0:
        max_fSOL_to_burn = nF * fSOL_staked_per
        fSOL_to_burn = -min(-fSOL_adjustment, max_fSOL_to_burn)
        return fSOL_to_burn
    return 0
