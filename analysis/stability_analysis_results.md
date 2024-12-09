# Analysis Results

## Overview
The analysis examines protocol behavior across different combinations of:
1. Stability Pool Activation Threshold (xSOL parameter)
2. Stability Mode Fee Parameter

## Parameter Definitions

### Stability Pool Activation (xSOL Parameter)
- Range: 1.1 to 1.6
- Represents the collateral ratio threshold at which hyUSD from stability pool is converted to xSOL
- Higher values mean earlier intervention (more conservative)
- Example: 1.3 means conversion triggers when CR falls to 130%

### Stability Mode Fee
- Range: 1.1 to 1.6
- Represents fee adjustments during stability mode: higher fees to discourage unwanted action (minting hyUSD, redeeming xSOL) and lower fees to encourage stabilizing actions (minting xSOL, redeeming hyUSD)
- Higher values mean earlier activation (more conservative)
- Example: 1.3 means fees are adjusted when CR falls below 130%

## Key Findings

### Depeg Events

1. **High Risk Zone**
   - Setting Stability Pool Activation CR at 110% (xSOL=1.1) is insufficient to prevent depegs
   - Depeg rate remains high (36-56%) regardless of Fee Activation CR
   - When stability pool intervention is set too low (110% CR), even activating fees at higher CR levels fails to significantly reduce depeg risk

2. **Safe Zone**
   - Setting Stability Pool Activation CR at 130% or higher prevents depegs completely
   - Critical threshold appears at 120% CR:
     * At 120% CR: near-zero depeg events
     * Below 120% CR: significant depeg risk

### Stability Pool Usage

1. **Activation Patterns**
   - Earlier stability pool intervention (higher Activation CR) leads to more frequent pool usage:
     * At Activation CR=160%: ~36 activations per run
     * At Activation CR=110%: only 2.8-5.8 activations per run

2. **Fee Impact**
   - Earlier fee adjustments (higher Fee Activation CR) correlate with decreased pool usage
   - This suggests that early fee adjustments help stabilize the system with fewer stability pool interventions needed
   - Most effective when combined with appropriate Stability Pool Activation CR (120-130%)

## Optimal Configuration Recommendations

1. **Safe Configuration**
   - Stability Pool Activation CR: 130%
   - Fee Activation CR: 140-150%
   - Results: Zero depegs with moderate pool usage (20-22 activations)

## Notable Observations

1. **Stability Pool Timing**
   - Earlier stability pool intervention (higher Activation CR) prevents depegs but requires more frequent pool usage
   - Late intervention (110% CR) fails to prevent depegs despite lower usage frequency

2. **Fee Adjustment Impact**
   - Fee adjustments alone have limited impact on preventing depegs
   - Primary effect is influencing the frequency of stability pool usage

## Conclusion
The analysis suggests that stability pool intervention should trigger at or above 120% CR for system safety. While earlier intervention ensures stability, it results in more frequent pool usage. The optimal balance appears to be around 130% CR for stability pool activation with fee adjustments starting at 140-150% CR, providing complete depeg protection with manageable pool activation frequency.