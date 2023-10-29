import torch
from dataset import CSVDataset
from torch.utils.data import DataLoader, random_split
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
import matplotlib.pyplot as plt
from datetime import datetime
from model import Model

if __name__ == "__main__":
    path = '../data/train.csv'
    #test_file_path = '../data/test.csv'
    dataset = CSVDataset(path)
    train_size = int(0.8 * len(dataset)) 
    test_size = len(dataset) - train_size  
    train, test = random_split(dataset, [train_size, test_size])
    
    train_dl = DataLoader(train, batch_size=32, shuffle=True)
    test_dl = DataLoader(test, batch_size=1024, shuffle=False)
    
    model = Model()
    
    criterion = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)