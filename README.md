# Hylo Modelisation Based on Historical Market Movements
## Overview
This project aims to model the behavior of the Hylo protocol based on historical market movements. By analyzing past data, we seek to understand how the protocol reacts under various market conditions, specifically focusing on the collateral ratio's impact on asset minting and burning.

## Assumptions in Pre-setup Modelisation
The model relies on the following key assumptions regarding the probability of net burn or mint of fSOL and xSOL after each trading day:

* **Collateral Ratio Impact:**
  * A higher collateral ratio increases the likelihood of fSOL being minted and xSOL being burned. This scenario suggests a market perception of increased security or over-collateralization, encouraging the minting of fSOL. Additionally, the low effective leverage of xSOL makes it less attractive to traders.
  * Conversely, a lower collateral ratio increases the likelihood of fSOL being burned and xSOL being minted. This situation reflects concerns over under-collateralization, leading fSOL holders to burn fSOL in order to redeem its equivalent value in SOL. It also signifies a growing interest among traders in xSOL, due to the higher effective leverage offered.

## Methodology
The model undergoes multiple iterations, with each run specifically designed to assess frequency of the stability pool usage and the frequency of negative xSOL price occurrences, negative xSOL signaling a failure in maintaining the collateralization of fSOL. Data collected after detecting a negative xSOL price are not considered in this model, as the protocol would require re-collateralization by the team to resume operations, a process not covered by this simulation.

### Evaluation Criteria:
* **Stability Pool Utilization vs. Negative xSOL Price Incidences:** We analyze the efficiency of different collateral ratios by comparing the ratio of stability pool calls to the instances of negative xSOL prices. A higher ratio indicates lesser efficiency of stability pool usage.

  * **Example:** If there are 1,000 calls to the stability pool for 50 instances of negative xSOL prices, the ratio is 20. Conversely, 500 stability pool calls for the same 50 instances of negative xSOL prices yield a ratio of 10. The latter scenario is much more efficient as it achieves the same number of negative xSOL price instances with half the stability pool usage.
* **Analysis of Negative xSOL Prices:** We also check the absolute number of instances where xSOL prices go negative as a direct measure of protocol performance under varying conditions.

## Limitations
This model primarily focuses on daily price returns, whereas, in practice, the protocol's stability would be monitored on a minute-by-minute basis. Consequently, the model may occasionally indicate under-collateralization situations that the protocol, in real-time operations, could effectively manage and mitigate.

Moreover, the model incorporates a stability pool mechanism, where fSOL is burned to redeem SOL, but it does not account for the conversion from fSOL to xSOL. This conversion process represents an additional strategy for the protocol to ensure stability, highlighting a significant aspect not covered in the current modeling approach.


## Usage of the Model

To utilize the model effectively, follow these steps in main.py to customize your simulation:

Update the following variables according to your requirements:
* Initial SOL collateral,
* Minimum Collateralization Ratio,
* Percentage of fSOL in the stability pool,
* Number of runs.

You can also change the burn/mint amount of xSOL/fSOL based on the collateralization ratio by adjusting the mean and standard deviation for different events in get_mint_amount().

Modify the likelihood of a burn/mint event for xSOL/fSOL according to the collateralization ratio by altering the percentages in get_action_probabilities().

To experience varying randomness across each run, you may comment out line 4: np.random.seed(7).

Once your setup is complete, execute the script by running python3 main.py. The results from the last run will be stored in a CSV file (simulation_results.csv).

For visualizing the results of the csv file, use the command python3 chart.py to generate a chart.

