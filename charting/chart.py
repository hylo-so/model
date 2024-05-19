import pandas as pd
import matplotlib.pyplot as plt

file_path = './simulation_results.csv' 
data = pd.read_csv(file_path)


# Plotting
fig, ax1 = plt.subplots(figsize=(10, 6))

color = 'tab:red'
ax1.set_xlabel('day')
ax1.set_ylabel('Marketcap (nF and nX)', color=color)
ax1.plot(data['day'], data['Marketcap fSOL'], label='Marketcap fSOL', color='r')
ax1.plot(data['day'], data['Marketcap xSOL'], label='Marketcap xSOL', color='b')
ax1.plot(data['day'], data['value of SOL in $'], label='value of SOL in $', color='orange')
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
color = 'tab:green'
ax2.set_ylabel('Collaterization ratio & nSOL', color=color) 
ax2.plot(data['day'], data['Collaterization ratio'], label='Collaterization ratio', color='g')
ax2.tick_params(axis='y', labelcolor=color)

ax2.set_ylim(0, 15)

# Added legends
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

fig.tight_layout() 
plt.title('Market Caps, Collaterization Ratio, and nSOL Evolution')

# Save the figure
plt.savefig('./market_caps_collaterization_ratio_nSOL_evolution.png')

plt.show()