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
        if fSOL_to_burn != 0:
            return fSOL_to_burn, True
    return 0, False

def adjust_fSOL_to_target_CR_2(nF, nX, nSOL, pX, pF, pSOL, stab_mod2):
    fSOL_SOL_mcap = nF * pF / pSOL  # Total fSOL market cap in SOL
    target_SOL = nSOL / stab_mod2
    SOL_moved = fSOL_SOL_mcap - target_SOL  # Correct calculation for SOL to move
    #print(target_SOL)
    #print(SOL_moved)
    if SOL_moved > 0:
        fSOL_burned = SOL_moved / (fSOL_SOL_mcap / nF)  # Amount of fSOL to burn
        xSOL_minted = -SOL_moved / (fSOL_SOL_mcap / nX)  # Amount of xSOL to mint
        return fSOL_burned, xSOL_minted
    return 0, 0

def use_stability_pool_2(nSOL, nF, fSOL_staked_per_2, stab_mod2, nX, pX, pF, pSOL_current):
    fSOL_burned, xSOL_minted = adjust_fSOL_to_target_CR_2(nF, nX, nSOL, pX, pF, pSOL_current, stab_mod2)
    if fSOL_burned > 0:
        max_fSOL_to_burn = nF * fSOL_staked_per_2
        fSOL_to_burn = min(fSOL_burned, max_fSOL_to_burn)
        xSOL_to_mint = fSOL_to_burn * (pSOL_current / pX)
        if fSOL_to_burn != 0:
            return fSOL_to_burn, xSOL_to_mint, True
    return 0, 0, False

#print(use_stability_pool_2(500, 400, 0.5, 1.251, 100, 1, 1, 1))