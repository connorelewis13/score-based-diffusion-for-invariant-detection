import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset

class FunctionDataset(Dataset):
    def __init__(self, data_path):
        df = pd.read_csv(data_path)

        in_cols  = [c for c in df.columns if c.startswith('in_')]
        out_cols = [c for c in df.columns if c.startswith('out_')]

        self.condition = torch.tensor(df[in_cols].values,  dtype=torch.float32)
        self.target    = torch.tensor(df[out_cols].values, dtype=torch.float32)

        self.n = self.target.shape[1]  # number of output variables

    def __len__(self):
        return len(self.target)

    def __getitem__(self, idx):
        return self.target[idx], self.condition[idx]