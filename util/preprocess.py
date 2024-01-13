import joblib
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler

CONTINUOUS_FEATURE_COLUMNS = ['TotRmsAbvGrd', 'WoodDeckSF', 'YrSold', '1stFlrSF']
CATEGORICAL_FEATURE_COLUMNS = ['Foundation', 'KitchenQual']
FEATURE_COLUMNS = CONTINUOUS_FEATURE_COLUMNS + CATEGORICAL_FEATURE_COLUMNS
LABEL_COLUMN = 'SalePrice'

SERIALIZER_EXTENSION = '.joblib'
ARTIFACTS_DIR = '../data/models'
SCALER_PATH = f'{ARTIFACTS_DIR}/scaler{SERIALIZER_EXTENSION}'
ONE_HOT_ENCODER_PATH = f'{ARTIFACTS_DIR}/one_hot_encoder{SERIALIZER_EXTENSION}'
MODEL_PATH = f'{ARTIFACTS_DIR}/model{SERIALIZER_EXTENSION}'

def preprocess(dataframe: pd.DataFrame, is_training: bool = False) -> pd.DataFrame:
    categorical_features_df = preprocess_categorical_features(dataframe, is_training)
    # df = dataframe.drop(CATEGORICAL_FEATURE_COLUMNS)
    final_df = dataframe[CONTINUOUS_FEATURE_COLUMNS].join(categorical_features_df)
    final_df['TotRmsAbvGrd'] = final_df['TotRmsAbvGrd'].astype(int)
    return dataframe[['Id']].join(final_df)

def preprocess_categorical_features(dataframe: pd.DataFrame, is_training: bool) -> pd.DataFrame:
    if is_training:
        one_hot_encoder = OneHotEncoder(handle_unknown='ignore', dtype='int')
        one_hot_encoder.fit(dataframe[CATEGORICAL_FEATURE_COLUMNS])
        joblib.dump(one_hot_encoder, ONE_HOT_ENCODER_PATH)
    else:
        one_hot_encoder = joblib.load(ONE_HOT_ENCODER_PATH)

    categorical_features_sparse = one_hot_encoder.transform(dataframe[CATEGORICAL_FEATURE_COLUMNS])
    categorical_features_df = pd.DataFrame.sparse.from_spmatrix(data=categorical_features_sparse,
                                                                columns=one_hot_encoder.get_feature_names_out(),
                                                                index=dataframe.index)
    return categorical_features_df

# if __name__ == "__main__":
#     # df = pd.read_csv('../../../data/folder_C/working_file_0.csv')
#     df = pd.read_csv('../../../data/train.csv')
#     _df = preprocess(df)
#     # _df.to_csv('../../../data/folder_C/vsfmlktmj.csv')
#     _df.to_csv('../../../data/folder_C/vsfmlktmj.csv',index=False, float_format='%.3f')
