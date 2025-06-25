import pandas as pd

def compute_churn_rate(df):
    if 'Churn' not in df.columns:
        return "No 'Churn' column found in your data.", None

    churn_rate = df['Churn'].mean() * 100
    retention_rate = 100 - churn_rate
    return (
        f"📉 Churn Rate: {churn_rate:.2f}%\n📈 Retention Rate: {retention_rate:.2f}%", 
        churn_rate
    )

def basic_summary(df):
    return {
        "Total Customers": len(df),
        "Columns": df.columns.tolist(),
        "Missing Values": int(df.isnull().sum().sum()),
        "Sample": df.head(3).to_dict()
    }
