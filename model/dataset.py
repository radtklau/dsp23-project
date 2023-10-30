from torch.utils.data import Dataset
import numpy as np
import json
import torch
import pandas as pd

class CSVDataset(Dataset):
    # load the dataset
    def __init__(self, path):
        try:
            with open(path, 'r') as json_file:
                self.data = pd.read_csv(path)
        except FileNotFoundError:
            pass

    # number of rows in the dataset
    def __len__(self):
        return len(self.data)

    # get a row at an index
    def __getitem__(self, idx):
        sample = self.data.iloc[idx].values
        return sample