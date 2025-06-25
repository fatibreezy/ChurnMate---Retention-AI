import streamlit as st
import pandas as pd
import requests
import json
from utils.churn_analysis import compute_churn_rate, basic_summary
st.set_page_config(page_title="ChurnMate - AI Retention Assistant", layout="centered")
st.title("🤖 ChurnMate: AI-Powered Customer Retention Assistant")

# Load API key from secrets
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
chat_endpoint = "https://openrouter.ai/api/v1/chat/completions"

# Sidebar
st.sidebar.header("📤 Upload Your Customer Data")
st.sidebar.markdown("""
Upload a customer dataset (CSV) containing at least a **Churn** column.  
ChurnMate will:
- Automatically analyze churn and retention rates
- Summarize your dataset
- Let you chat with an AI assistant about churn reduction, customer growth, and retention strategies
""")
import io

# Add a richer sample dataset
sample_data = pd.DataFrame({
    "CustomerID": ["C001", "C002", "C003", "C004", "C005", "C006", "C007"],
    "Gender": ["Female", "Male", "Female", "Male", "Female", "Male", "Female"],
    "Age": [25, 31, 40, 29, 33, 45, 27],
    "SubscriptionType": ["Basic", "Premium", "Standard", "Standard", "Premium", "Basic", "Premium"],
    "MonthlyFee": [29.99, 59.99, 39.99, 39.99, 59.99, 29.99, 59.99],
    "JoinDate": ["2023-01-10", "2022-05-20", "2021-09-15", "2023-03-05", "2022-11-01", "2021-12-12", "2023-04-10"],
    "Churn": ["No", "Yes", "No", "No", "Yes", "No", "Yes"]
})

# Convert to downloadable CSV
sample_csv = io.StringIO()
sample_data.to_csv(sample_csv, index=False)

# Add download button
st.sidebar.download_button(
    label="📥 Download Sample Customer Data",
    data=sample_csv.getvalue(),
    file_name="sample_customer_data.csv",
    mime="text/csv"
)

uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
df = None

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("✅ File uploaded successfully!")
    st.subheader("📊 Customer Data Preview")
    st.dataframe(df.head())

    summary = basic_summary(df)
    st.markdown("### 🔍 Dataset Summary")
    st.write(summary)

    st.markdown("### 📈 Churn Metrics")
    churn_text, churn_rate = compute_churn_rate(df)
    st.info(churn_text)

    # ✅ Automatically get AI advice after churn rate is displayed
    st.markdown("### 💡 AI Retention Advice")
    with st.spinner("Generating AI-powered business advice..."):
        advice_prompt = f"My churn rate is {churn_rate:.2f}%. What advice can you give to reduce churn and improve customer retention?"

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        advice_messages = [
            {"role": "system", "content": "You are an expert in customer churn, retention strategies, and business growth."},
            {"role": "user", "content": advice_prompt}
        ]

        advice_response = requests.post(chat_endpoint, headers=headers, data=json.dumps({
            "model": "mistralai/mistral-7b-instruct",
            "messages": advice_messages
        }))

        if advice_response.status_code == 200:
            ai_advice = advice_response.json()["choices"][0]["message"]["content"]
            st.success(f"**🤖 ChurnMate says:** {ai_advice}")
        else:
            st.warning("Could not generate advice at the moment. Try again later or use the chatbot.")

st.markdown("---")
st.subheader("💬 Chat with ChurnMate")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "You are a helpful AI assistant for analyzing customer churn, advising on retention strategies, and supporting business growth decisions."}
    ]

user_input = st.text_input("Ask me anything about churn, retention, or customer success:")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    submit = st.button("🤖 Ask ChurnMate")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": st.session_state.chat_history
    }

    response = requests.post(chat_endpoint, headers=headers, data=json.dumps(body))

    if response.status_code == 200:
        reply = response.json()["choices"][0]["message"]["content"]
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.markdown(f"**🤖 ChurnMate:** {reply}")
    else:
        st.error("❌ Failed to fetch response. Please try again later.")
        st.write("Debug info:", response.text)  

if st.session_state.chat_history:
    with st.expander("🕒 Conversation History"):
        for msg in st.session_state.chat_history[1:]:
            role = "You" if msg["role"] == "user" else "ChurnMate"
            st.markdown(f"**{role}:** {msg['content']}")
