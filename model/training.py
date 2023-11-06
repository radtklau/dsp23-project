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
    path = 'data/train.csv'
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
    
    training_loss = []
    
    # enumerate epochs
    for epoch in tqdm(range(1000)):
        running_loss = 0.0
        # enumerate mini batches
        for i, (inputs, targets) in enumerate(train_dl):
            # clear the gradients
            optimizer.zero_grad()
            # compute the model output
            yhat = model(inputs)
            # calculate loss
            loss = criterion(yhat, targets)
            # credit assignment
            loss.backward()
            # update model weights
            optimizer.step()
            
            running_loss += loss.item()
        
        epoch_loss = running_loss / len(train_dl)
        training_loss.append(epoch_loss)
        
    epochs = range(1, len(training_loss) + 1)
    
    plt.plot(epochs, training_loss, label='Training Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training Loss Over Time')
    plt.legend()

    # Show the plot or save it to a file
    
    current_datetime = datetime.now()
    file_name = current_datetime.strftime('plots/%Y%m%d%H%M%S_training_loss_0.png')
    plt.savefig(file_name)
    plt.show()
    torch.save(model.state_dict(), 'trained_model_0.pth')