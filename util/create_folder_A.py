import pandas as pd
import os

if __name__ == "__main__":
    path = "../data/train.csv"
    data = pd.read_csv(path)
    # os.mkdir("../data/folder_A")
    
    for file in range(1000):
        num_random_rows = 10
        random_rows = data.sample(n=num_random_rows)

        file_name = "file_"+str(file)+".csv"
        folder_A_path = "../data/folder_A/"
        random_rows.to_csv(folder_A_path+file_name, index=False)
