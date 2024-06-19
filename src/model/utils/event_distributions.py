import numpy as np
import configparser

def get_action_probabilities(collateral_ratio: float, stab_mode_fees_control: float) -> dict:
    """
    Define the probability distribution for actions based on collateral ratio.

    Args:
        collateral_ratio (float): The current collateral ratio.
        stab_mode_fees_control (float): The fees control stability mode collateral ratio activation threshold

    Returns:
        dict: A dictionary with probabilities for minting hyUSD and xSOL based on the current collateral ratio.
    """
    if collateral_ratio > 5:
        return {'hyUSD_mint': 1, 'xSOL_mint': 0.10}
    elif 3 < collateral_ratio <= 5:
        return {'hyUSD_mint': 0.90, 'xSOL_mint': 0.25}
    elif 2.2 < collateral_ratio <= 3:
        return {'hyUSD_mint': 0.8, 'xSOL_mint': 0.40}
    elif stab_mode_fees_control < collateral_ratio <= 2.2:
        return {'hyUSD_mint': 0.60, 'xSOL_mint': 0.6}
    elif 1 < collateral_ratio <= stab_mode_fees_control:
        return {'hyUSD_mint': 0.00, 'xSOL_mint': 0.80}
    else:
        return {'hyUSD_mint': 0.00, 'xSOL_mint': 1.00}

def get_mint_amount(collateral_ratio: float, config: configparser.ConfigParser) -> dict:
    """
    Determine mint and burn amounts for hyUSD and xSOL based on the collateral ratio and configuration.

    Args:
        collateral_ratio (float): The current collateral ratio.
        config (configparser.ConfigParser): Configuration parser with mint and burn settings.

    Returns:
        dict: A dictionary with mint and burn amounts for hyUSD and xSOL.
    """
    # Determine the section prefix based on the collateral ratio
    section_prefix = determine_section_prefix(collateral_ratio)

    # Fetch the values using the correct section and keys
    hyUSD_mint_mean = config.getfloat('mint_amount', f'{section_prefix}_hyUSD_mint_mean')
    hyUSD_mint_std = config.getfloat('mint_amount', f'{section_prefix}_hyUSD_mint_std')
    xSOL_mint_mean = config.getfloat('mint_amount', f'{section_prefix}_xSOL_mint_mean')
    xSOL_mint_std = config.getfloat('mint_amount', f'{section_prefix}_xSOL_mint_std')
    hyUSD_burn_mean = config.getfloat('mint_amount', f'{section_prefix}_hyUSD_burn_mean')
    hyUSD_burn_std = config.getfloat('mint_amount', f'{section_prefix}_hyUSD_burn_std')
    xSOL_burn_mean = config.getfloat('mint_amount', f'{section_prefix}_xSOL_burn_mean')
    xSOL_burn_std = config.getfloat('mint_amount', f'{section_prefix}_xSOL_burn_std')

    return {
        'hyUSD_mint_amount': np.random.normal(hyUSD_mint_mean, hyUSD_mint_std), 
        'xSOL_mint_amount': np.random.normal(xSOL_mint_mean, xSOL_mint_std),
        'hyUSD_burn_amount': np.random.normal(hyUSD_burn_mean, hyUSD_burn_std),
        'xSOL_burn_amount': np.random.normal(xSOL_burn_mean, xSOL_burn_std)
    }

def determine_section_prefix(collateral_ratio: float) -> str:
    """
    Determine the section prefix for configuration values based on the collateral ratio.

    Args:
        collateral_ratio (float): The current collateral ratio.

    Returns:
        str: The section prefix used for fetching configuration values.
    """
    if collateral_ratio > 5:
        return 'CR5'
    elif 3 < collateral_ratio <= 5:
        return 'CR3-5'
    elif 2.2 < collateral_ratio <= 3:
        return 'CR22-3'
    elif 1 < collateral_ratio <= 2.2:
        return 'CRmode2-22'
    else:
        return 'CR1-mode2'
