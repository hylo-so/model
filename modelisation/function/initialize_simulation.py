# initialize_simulation.py

def initialize_simulation(pSOL_initial, amount_SOL_initial):
    # Prices of fSOL and xSOL start at 1
    pF = 1  
    pX = 1  
    
    # Calculate nF and nX based on the initial SOL reserve and prices
    nSOL = amount_SOL_initial  # SOL in reserve
    nF = (pSOL_initial * nSOL) / 2
    nX = nF

    return nSOL, nF, nX, pF, pX
