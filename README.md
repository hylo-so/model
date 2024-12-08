# Hylo Modelisation

## Overview
This project aims to model the behavior of the Hylo protocol. By analyzing past data and simulated future returns using a Monte Carlo model, it seeks to understand how the protocol reacts under various market conditions, specifically focusing on the collateral ratio's impact on asset minting and burning.

## Assumptions in Pre-setup Modelisation
The model relies on the following key assumptions regarding the probability of net burn or mint of hyUSD and xSOL after each trading day:

- **Collateral Ratio Impact:**
  - A higher collateral ratio increases the likelihood of hyUSD being minted and xSOL being burned. This scenario suggests a market perception of increased security or over-collateralization, encouraging the minting of hyUSD. Additionally, the low effective leverage of xSOL makes it less attractive to traders.
  - Conversely, a lower collateral ratio increases the likelihood of hyUSD being burned and xSOL being minted. This situation reflects concerns over under-collateralization, leading hyUSD holders to burn hyUSD in order to redeem its equivalent value in SOL. It also signifies a growing interest among traders in xSOL, due to the higher effective leverage offered.

## Methodology
The model undergoes multiple iterations, with each run specifically designed to assess the frequency of the stability pool usage and the frequency of negative xSOL price occurrences. Negative xSOL signaling a failure in maintaining the collateralization of hyUSD. Data collected after detecting a negative xSOL price are not considered in this model, as the protocol would require re-collateralization by the team to resume operations, a process not covered by this simulation.

## Limitations

The model has several important limitations to consider:

### Time Resolution
- The model operates on daily price returns, while the actual protocol monitors and responds to market conditions in real-time
- This limitation may lead to the model indicating under-collateralization scenarios that the protocol could prevent in practice through its real-time monitoring and response mechanisms

### Stability Mechanisms
The model does not incorporate several key stability mechanisms of the protocol:

1. **Redemptions Bonuses**
   - In stability mode, the protocol can offer bonus on hyUSD redemptions
   - These bonuses create arbitrage opportunities where traders can profit by:
     - Buying hyUSD at market price (e.g. $1)
     - Redeeming it directly through the protocol with a bonus (e.g. $1.01)
   - This mechanism helps restore the collateral ratio by incentivizing hyUSD purchases on the open market and redemptions through the protocol

2. **Fee-Based Recollateralization**
   - The protocol accumulates fees from normal operations
   - These accumulated fees can be used as a last-resort mechanism to recollateralize the system
   - This provides an additional safety net not reflected in the current model

## Setup and Usage

### Prerequisites
- Ensure you have [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) installed on your system.

### Installation

1. **Clone the repository**  
git clone <https://github.com/hylo-so/model.git> 

2. **Create the Conda environment**  
Create a Conda environment using the `environment.yml` file provided in the project:
`conda env create -f environment.yml`


3. **Activate the environment**  
Activate the Conda environment:
`conda activate <env-name>`


### Running the Model
first go to src folder, run
`cd src`

then to execute the model, run:
`python3 src/main.py`

This will launch the model with the default parameters. To customize these parameters, edit `config.ini` and update the following variables as needed:

- `beta`: The beta parameter of the Monte Carlo simulation.
- `T`: The number of days for the Monte Carlo simulation.
- `N`: The number of different price paths generated.
- `sModeLower`: The lower stability mode collateral ratio threshold to test.
- `sModeUpper`: The highest stability mode collateral ratio threshold to test.
- `sModeStep`: The step size between tests of different stability modes.
- `amount_SOL_initial`: The initial amount of SOL in the collateral pool.
- `hyUSD_staked_per`: The percentage of hyUSD staked in the stability pool.
- `num_runs_per_path`: The number of runs of the model on each path.
- `[action_probabilities]` defines the probability of a mint or burn action occurring, depending on the Collateral Ratio. For example, `CR3-5_hyUSD_mint` specifies the probability of hyUSD being minted when the Collateral Ratio is between 3 and 5.
- `[mint_amount]` defines the normal distribution parameters for the amount of tokens minted or burned. For instance, `CR3-5_hyUSD_mint_mean` and `CR3-5_hyUSD_mint_std` specify the mean and standard deviation, respectively, of the normal distribution for the amount of hyUSD minted when the Collateral Ratio is between 3 and 5.

### Running the Analysis

After running the model, you can analyze the results using the provided analysis tools:

1. **Navigate to the analysis folder**:
`cd analysis`

2. **Run the analysis script**:
`python3 analysis.py`

This will generate two CSV files in the `output` directory:
- `detailed_results.csv`: Contains detailed data for each simulation run
- `summary_results.csv`: Contains aggregated statistics grouped by parameters

- To visualize the results as heatmaps:
`python3 create_heatmaps.py`

This will generate `parameter_analysis_heatmaps.png` in the `output` directory, showing:
- Depeg Event Rate heatmap: Displays the probability of depeg events for different parameter combinations
- Stability Pool Usage heatmap: Shows the average number of stability pool activations

### Understanding the Analysis Results

The analysis provides several key metrics:

1. **Depeg Events**:
   - Frequency of situations where the collateral ratio falls below 1
   - Impact of different xSOL and fee parameters on system stability

2. **Stability Pool Usage**:
   - Number of times the stability pool was activated
   - Average activations across different parameter combinations




