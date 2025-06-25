import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

def train_churn_model(df):
    if 'Churn' not in df.columns:
        return "Dataset must contain a 'Churn' column.", None

    df = df.dropna()
    df_encoded = df.copy()

    for col in df.select_dtypes(include=['object']).columns:
        df_encoded[col] = LabelEncoder().fit_transform(df[col])

    X = df_encoded.drop("Churn", axis=1)
    y = df_encoded["Churn"]

    model = LogisticRegression()
    model.fit(X, y)
    
    return model, X.columns.tolist()

def predict_churn(model, input_data):
    return model.predict_proba([input_data])[0][1] * 100
