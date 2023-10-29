import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import torch

#TODO add more layers

class LR_Model(nn.Module):
    def __init__(self):
        super(LR_Model, self).__init__()
        self.layer = nn.Linear(4, 2)  # Three inputs and two outputs
        self.activation = F.sigmoid

    def forward(self, x):
        x = x.to(torch.float32)
        out = self.activation(self.layer(x))
        return out