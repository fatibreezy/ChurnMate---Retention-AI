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

st.markdown("---")
st.subheader("💬 Chat with ChurnMate")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "You are a helpful AI assistant for analyzing customer churn, advising on retention strategies, and supporting business growth decisions."}
    ]

user_input = st.text_input("Ask me anything about churn, retention, or customer success:")

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
