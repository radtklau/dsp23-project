from torch.utils.data import Dataset
import numpy as np
import torch
import pandas as pd
from sklearn.impute import SimpleImputer

class CSVDataset(Dataset):
    def __init__(self, csv_file):
        self.data = pd.read_csv(csv_file)
        self.features = self.data.drop(columns=['SalePrice','Id']).values  # Extract feature columns as numpy array
        self.targets = self.data['SalePrice'].values  # Extract target column as numpy array
        self.preprocess_data()
        
    def preprocess_data(self):
        #missing numerical values are replaced by taking average of existing values
        #missing categorical values are replaced by taking most common of existing values
        
        #1. remove samples with missing SalePrice
        missing_values_mask = np.isnan(self.targets)
        self.features = self.feature[~missing_values_mask]
        self.targets = self.targets[~missing_values_mask]
        
        #2. fill in missing values
        numerical_imputer = SimpleImputer(strategy='mean')
        num_col_ind = []
        cat_col_name = []
        
        for ind, column in enumerate(self.features):
            if all(np.char.isnumeric(column[1:])):
                num_col_ind.append(ind)
            else:
                cat_col_name.append(column[0])
                
        self.features[:, num_col_ind] = numerical_imputer.fit_transform(\
            self.features[:, num_col_ind])
    
        for column_name in cat_col_name:
                column_index = self.data.columns.get_loc(column_name)
                self.features[:, column_index] = self.fill_missing_categorical(\
                    self.features[:, column_index])
                
        #3. encode categorical values
        
        
    
    def fill_missing_categorical(self, column):
        most_common_value = column.mode().values[0]  # Get the most common value
        return column.fillna(most_common_value)
            
            
               
        
        pass
        

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        feature = self.features[idx]
        target = self.targets[idx]
        return feature, target
