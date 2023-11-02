from torch.utils.data import Dataset
import numpy as np
import torch
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder
from sklearn.preprocessing import OneHotEncoder

class CSVDataset(Dataset):
    def __init__(self, csv_file):
        self.data = pd.read_csv(csv_file)
        #self.features = self.data.drop(columns=['SalePrice','Id']).values  # Extract feature columns as numpy array
        self.targets = self.data['SalePrice'].values  # Extract target column as numpy array
        self.feat_ordinal_dict = {
            # Considers 'missing' as 'neutral'
            # Take the order is important as the ordinal encoders will label the categories in the order of the list.
            'BsmtCond': ['missing', 'Po', 'Fa', 'TA', 'Gd'],
            'BsmtExposure': ['missing', 'No', 'Mn', 'Av', 'Gd'],
            'BsmtFinType1': ['missing', 'Unf', 'LwQ', 'Rec', 'BLQ', 'ALQ', 'GLQ'],
            'BsmtFinType2': ['missing', 'Unf', 'LwQ', 'Rec', 'BLQ', 'ALQ', 'GLQ'],
            'BsmtQual': ['missing', 'Fa', 'TA', 'Gd', 'Ex'],
            'Electrical': ['missing', 'Mix', 'FuseP', 'FuseF', 'FuseA', 'SBrkr'],
            'ExterCond': ['missing', 'Po', 'Fa', 'TA', 'Gd', 'Ex'],
            'ExterQual': ['missing', 'Fa', 'TA', 'Gd', 'Ex'],
            'FireplaceQu': ['missing', 'Po', 'Fa', 'TA', 'Gd', 'Ex'],
            'Functional': ['missing', 'Sev', 'Maj2', 'Maj1', 'Mod', 'Min2', 'Min1', 'Typ'],
            'GarageCond': ['missing', 'Po', 'Fa', 'TA', 'Gd', 'Ex'],
            'GarageFinish': ['missing', 'Unf', 'RFn', 'Fin'],
            'GarageQual': ['missing', 'Po', 'Fa', 'TA', 'Gd', 'Ex'],
            'HeatingQC': ['missing', 'Po', 'Fa', 'TA', 'Gd', 'Ex'],
            'KitchenQual': ['missing', 'Fa', 'TA', 'Gd', 'Ex'],
            'LandContour': ['missing', 'Low', 'Bnk', 'HLS', 'Lvl'],
            'LandSlope': ['missing', 'Sev', 'Mod', 'Gtl'],
            'LotShape': ['missing', 'IR3', 'IR2', 'IR1', 'Reg'],
            'PavedDrive': ['missing', 'N', 'P', 'Y'],
        }
        
        self.features = self.preprocess_data()
    
    def preprocess_data(self):
        numerical_imputer = SimpleImputer(strategy='mean')
        #replacing missing values and unifiying dtypes
        
        #1. replace nan with 'NA' in categorical variables (if dtype == object)
        for column in self.data:
            if self.data[column].dtype == object: #categorical feature
                self.data[column] = self.data[column].fillna('NA')  
        #2. handle GarageYrBlt seperatly
            elif column == 'GarageYrBlt': #NaN means no garage, construction year of 0 would not be a good idea so we take mean
                numerical_imputer.fit_transform(self.data[column])
        #3. Convert all numerical data to float64 and replace NaN with 0.0
            else:
                if np.issubdtype(self.data[column].dtype, np.integer):
                    self.data[column] = self.data[column].astype('float64')
                self.data[column] = self.data[column].fillna(0.0)
                
        #encoding categorical data
        
        
                  
                     
    
    """
    def preprocess_data(self):
            num_col_name = []
            cat_col_name = []
            
            for ind, column in enumerate(self.data.columns):
                if any(np.char.isnumeric(column[1:])):
                    num_col_name.append(column[0])
                else:
                    cat_col_name.append(column[0])
                    
            # Encode ordinal features
            ordinal_columns = list(self.feat_ordinal_dict.keys())
            ordinal_encoder = OrdinalEncoder(categories=[self.feat_ordinal_dict[col] for col in ordinal_columns])

            for col in ordinal_columns:
                self.data[col] = ordinal_encoder.fit_transform(self.data[col].values.reshape(-1, 1))
            
            
            # Encode nominal features with one-hot encoding
            nominal_columns = [col for col in self.data.columns if col not in ordinal_columns and col in num_col_name]
            nominal_encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')

            nominal_encoded = nominal_encoder.fit_transform(self.data[nominal_columns])


            # Remove original nominal columns
            self.data = self.data.drop(columns=nominal_columns)

            # Concatenate one-hot encoded features with the original data
            self.data = pd.concat([self.data, pd.DataFrame(nominal_encoded, columns=nominal_encoder.get_feature_names(nominal_columns))], axis=1)

            # Extract features as a NumPy array
            features = self.data.drop(columns=['SalePrice', 'Id']).values

            return features
    """
    """   
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
            if any(np.char.isnumeric(column[1:])):
                num_col_ind.append(ind)
            else:
                cat_col_name.append(column[0])      
        self.features[:, num_col_ind] = numerical_imputer.fit_transform(\
            self.features[:, num_col_ind])

        #not necessary as NA doesnt mean the data is missing but the absence of 
        #the feature in the house
        
        for column_name in cat_col_name:
                column_index = self.data.columns.get_loc(column_name)
                self.features[:, column_index] = self.fill_missing_categorical(\
                    self.features[:, column_index])       
        #3. encode categorical ordinal values
        ordinal_columns = list(self.feat_ordinal_dict.keys())
        ordinal_encoder = OrdinalEncoder(categories=[self.feat_ordinal_dict[col] \
            for col in ordinal_columns])
        
        for col in ordinal_columns:
            col_index = self.data.columns.get_loc(col)
            self.features[:, col_index] = ordinal_encoder.fit_transform( \
                self.features[:, col_index].reshape(-1, 1))
        
        #4. encode categorical nominal values 

        pass
        """
        
    """
    def fill_missing_categorical(self, column):
        most_common_value = column.mode().values[0]  # Get the most common value
        return column.fillna(most_common_value)
    """      
            
        

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        feature = self.features[idx]
        target = self.targets[idx]
        return feature, target
