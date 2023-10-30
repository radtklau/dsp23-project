from torch.utils.data import Dataset
import numpy as np
import torch
import pandas as pd

class CSVDataset(Dataset):
    def __init__(self, csv_file):
        self.data = pd.read_csv(csv_file)
        self.features = self.data.drop(columns=['SalePrice']).values  # Extract feature columns as numpy array
        self.targets = self.data['SalePrice'].values  # Extract target column as numpy array

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = {
            'features': torch.tensor(self.features[idx], dtype=torch.float),
            'target': torch.tensor(self.targets[idx], dtype=torch.float)
        }
        return sample
