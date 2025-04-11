# Parameter Analysis Results

## Overview

This analysis examines the protocol's behavior under different parameter configurations based on historical SOL price data. The key parameters analyzed are:

1. **Stability Mode 2 -- Stability Pool**: The collateral ratio threshold at which hyUSD from the stability pool is converted to xSOL
2. **Stability Mode 1 -- Fee Adjustment**: The collateral ratio threshold for fee adjustments during stability mode

## Key Findings

### Depeg Event Rate

The depeg event rate shows the probability of the collateral ratio falling below 1:

- **High Risk Zone (CR ≤ 1.25)**:
  - At 1.1 CR: 100% depeg rate across all fee parameter values
  - At 1.15 CR: 91.7-100% depeg rate
  - At 1.2 CR: 75-100% depeg rate
  - At 1.25 CR: 50-62.5% depeg rate

- **Safe Zone (CR ≥ 1.3)**:
  - Complete system stability with 0% depeg events
  - This threshold represents a critical safety boundary

- **Transition Point**:
  - The most significant improvement occurs between 1.25 and 1.3 CR
  - This represents the optimal safety threshold for the protocol

### Stability Pool Activations

The average number of stability pool activations per simulation:

- **Low CR Settings (1.1-1.2)**:
  - Relatively few activations (3.1-16.7)
  - This is likely because the system quickly depegs before many activations can occur

- **Mid-Range CR (1.25-1.35)**:
  - Moderate activation frequency (21.9-41.9)
  - Represents a balance between stability and efficiency

- **High CR Settings (1.4-1.55)**:
  - Highest activation frequency (34.8-47.8)
  - More frequent interventions lead to better stability but higher operational overhead

- **Activation Pattern**:
  - Stability pool activations generally increase as the Stability Mode 2 threshold activation parameter increases
  - Higher fee parameters don't consistently reduce activations, suggesting the Stability Mode 2 threshold activation parameter is more influential

### Activation Frequency as Percentage

With the simulation running over 1000 days of price data, we can express the stability pool activation frequency as a percentage of total days:

- **Low CR Settings (1.1-1.2)**: 0.3-1.7% of days require stability pool activation
- **Mid-Range CR (1.25-1.35)**: 2.2-4.2% of days require stability pool activation
- **High CR Settings (1.4-1.55)**: 3.5-4.8% of days require stability pool activation

This means that even in the most active configuration, the stability pool is only triggered on less than 5% of days, indicating relatively low operational overhead.

## Parameter Analysis Heatmaps

![Parameter Analysis Heatmaps](output/analysis/parameter_analysis_heatmaps.png)

The heatmaps above illustrate:
- **Left**: Depeg Event Rate - Shows the probability of depeg events for different parameter combinations
- **Right**: Average Stability Pool Activations - Shows the frequency of stability pool interventions

## Optimal Configuration Recommendations

Based on that analysis, we recommend the following configurations:

### 1. Minimum parameter threshold for complete system stability
- **Stability Mode 2 -- Stability Pool**: 1.3
- **Stability Mode 1 -- Fee Adjustment**: 1.3
- **Results**: 0% depeg risk with ~42 activations per run (4.2% of days)
- **Rationale**: This configuration guarantees complete system stability with the minimum threshold

### 2. Limited Stability Pool Activations & complete system stability
- **Stability Mode 2 -- Stability Pool**: 1.3
- **Stability Mode 1 -- Fee Adjustment**: 1.45-1.5
- **Results**: 0% depeg risk with ~32-35 activations per run (3.2-3.5% of days)
- **Rationale**: Maintains complete stability while reducing activation frequency by ~25%

## Model Limitations

It's important to note some limitations of this analysis:

- **Time Granularity**: The model operates on daily price data, which may overstate depeg risks. In a production environment, the protocol is monitored on a second-by-second basis, allowing for much faster responses to price movements.
- **Discrete Interventions**: The simulation applies stability mechanisms at fixed daily intervals, whereas the actual protocol can respond continuously to market conditions.

These limitations suggest that the actual protocol may perform better than indicated by the model, particularly in preventing depegs during sudden price movements.

## Conclusion

The data demonstrates that a critical safety threshold exists at 1.3 CR for the Stability Mode 2 parameter. Below this threshold, the system experiences significant depeg events, while at or above this level, the system maintains complete stability.

The Stability Mode 1 (fee) parameter has a secondary but still important effect, primarily influencing the frequency of stability pool activations rather than preventing depegs entirely. Setting the fee parameter higher than the stability pool parameter (by about 0.15-0.2) provides the best balance between stability and operational efficiency.