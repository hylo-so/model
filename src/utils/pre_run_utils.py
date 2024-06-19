import os
import shutil
import pandas as pd
import numpy as np

def clear_output_directory(directory_path: str):
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

def count_decimal_places(value):
    text = str(value)
    if '.' in text:
        return len(text.split('.')[1])
    return 0

def clean_price_csv(input_price_csv: str, T: int) -> np.ndarray:
    price_df = pd.read_csv(input_price_csv, usecols=['Price'])
    price_df['Price'] = price_df['Price'].replace(',', '', regex=True).astype(float)
    price_paths = price_df['Price'].values[:T].reshape(-1, 1)
    return price_paths
