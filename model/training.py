import torch
from dataset import CSVDataset
from torch.utils.data import DataLoader, random_split
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
import matplotlib.pyplot as plt
from datetime import datetime

if __name__ == "__main__":
    train_file_path = '../data/train.csv'
    test_file_path = '../data/test.csv'
    train_dataset = CSVDataset(train_file_path)
    test_dataset = CSVDataset(test_file_path)