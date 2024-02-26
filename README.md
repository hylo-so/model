# Hylo Modelisation

## Overview
This project aims to model the behavior of the Hylo protocol. By analyzing past data and simulated future returns using a Monte Carlo model, it seeks to understand how the protocol reacts under various market conditions, specifically focusing on the collateral ratio's impact on asset minting and burning.

## Assumptions in Pre-setup Modelisation
The model relies on the following key assumptions regarding the probability of net burn or mint of fSOL and xSOL after each trading day:

- **Collateral Ratio Impact:**
  - A higher collateral ratio increases the likelihood of fSOL being minted and xSOL being burned. This scenario suggests a market perception of increased security or over-collateralization, encouraging the minting of fSOL. Additionally, the low effective leverage of xSOL makes it less attractive to traders.
  - Conversely, a lower collateral ratio increases the likelihood of fSOL being burned and xSOL being minted. This situation reflects concerns over under-collateralization, leading fSOL holders to burn fSOL in order to redeem its equivalent value in SOL. It also signifies a growing interest among traders in xSOL, due to the higher effective leverage offered.

## Methodology
The model undergoes multiple iterations, with each run specifically designed to assess the frequency of the stability pool usage and the frequency of negative xSOL price occurrences. Negative xSOL signaling a failure in maintaining the collateralization of fSOL. Data collected after detecting a negative xSOL price are not considered in this model, as the protocol would require re-collateralization by the team to resume operations, a process not covered by this simulation.

## Limitations
This model primarily focuses on daily price returns, whereas, in practice, the protocol's stability would be monitored on a minute-by-minute basis. Consequently, the model may occasionally indicate under-collateralization situations that the protocol, in real-time operations, could effectively manage and mitigate.

Moreover, the model incorporates a stability pool mechanism, where fSOL is burned to redeem SOL, but it does not account for the conversion from fSOL to xSOL. This conversion process represents an additional strategy for the protocol to ensure stability, highlighting a significant aspect not covered in the current modeling approach.

## Setup and Usage

### Prerequisites
- Ensure you have [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) installed on your system.

### Installation

1. **Clone the repository**  
git clone <https://github.com/hylo-so/model.git> 

2. **Create the Conda environment**  
Create a Conda environment using the `environment.yml` file provided in the project:
`conda <env-name> create -f environment.yml`


3. **Activate the environment**  
Activate the Conda environment:
`conda activate <env-name>`


### Running the Model
To execute the model, run:
`python3 main.py`

This will launch the model with the default parameters. To customize these parameters, edit `main.py` and update the following variables as needed:
- `beta`: The beta parameter of the Monte Carlo simulation.
- `T`: The number of days for the Monte Carlo simulation.
- `N`: The number of different price paths generated.
- `stab_mod1_range`: The activation range for Stability Mode 1 to test.
- `stab_mod2_range`: The activation range for Stability Mode 2 to test.
- `num_runs_per_path`: The number of runs of the model on each path.

Upon completion, two heat maps will be displayed showing the percentage of time that a run has faced a de-collateralization event, and the percentage of time the stability pool has been utilized for different combinations of stability mod.
