import pandas as pd
from sklearn.preprocessing import LabelEncoder
def get_data(dir):
    labelencoder = LabelEncoder()
    df = pd.read_csv(dir)
    object_columns = df.select_dtypes(include=['object']).columns.tolist()
    for column in object_columns:
        df[column] = labelencoder.fit_transform(df[column])
    return df