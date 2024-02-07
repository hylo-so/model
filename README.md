# Hylo Modelisation Based on Historical Market Movements
## Overview
This project aims to model the behavior of the Hylo protocol based on historical market movements. By analyzing past data, we seek to understand how the protocol reacts under various market conditions, specifically focusing on the collateral ratio's impact on asset minting and burning.

## Assumptions in Pre-setup Modelisation
The model relies on the following key assumptions regarding the probability of net burn or mint of fSOL and xSOL after each trading day:

* **Collateral Ratio Impact:**
  * A higher collateral ratio increases the likelihood of fSOL being minted and xSOL being burned. This scenario suggests a market perception of increased security or over-collateralization, encouraging the minting of fSOL.
  * Conversely, a lower collateral ratio heightens the probability of fSOL being burned and xSOL being minted. This reflects concerns over under-collateralization, prompting adjustments to restore balance.

## Methodology
The model undergoes multiple iterations, with each run specifically designed to assess the operational dynamics of the stability pool and the frequency of negative xSOL price occurrences, which signals a failure in maintaining the collateralization of fSOL.

### Evaluation Criteria:
* **Stability Pool Utilization vs. Negative xSOL Price Incidences:** We analyze the efficiency of different collateral ratios by comparing the ratio of stability pool calls to the instances of negative xSOL prices. A higher ratio indicates lesser efficiency of stability pool usage.

  * **Example:** If there are 1,000 calls to the stability pool for 50 instances of negative xSOL prices, the ratio is 20. Conversely, 500 stability pool calls for the same 50 instances of negative xSOL prices yield a ratio of 10. The latter scenario is deemed more efficient as it achieves the same number of negative xSOL price instances with half the stability pool usage.
* **Analysis of Negative xSOL Prices:** We also scrutinize the absolute number of instances where xSOL prices go negative as a direct measure of protocol performance under varying conditions.
