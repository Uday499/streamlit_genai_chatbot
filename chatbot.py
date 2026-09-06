from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq
import pandas as pd


def get_dataframe_info(df):

    return df.to_string(index=False)

# load env variables
load_dotenv()


#streamlit page setup

st.set_page_config(
    page_title = "Chatbot", 
    page_icon = "🤖",
    layout = "centered"
)

st.title("🤖 Generative AI Chatbot")

uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.success(
        f"CSV loaded successfully! {len(df)} rows and {len(df.columns)} columns."
    )

    st.dataframe(df)

    dataframe_info = get_dataframe_info(df)

    st.write("### Dataset Information")
    st.code(dataframe_info)

# initiate chat_history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# doing this because stream lit run from the begining after every interaction(not reload button, 
# but once the prompt is sent by the user).
#to store chat histroy


# show chathistory

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


## initiate llm

llm = ChatGroq(
    model = "groq/compound-mini",
    temperature = 0.0
)



# creates user prompt on the UI
user_prompt = st.chat_input("Ask Chatbot...")

if user_prompt:

    st.chat_message("user").markdown(user_prompt)

    plan = create_analysis_plan(
        llm,
        user_prompt,
        dataframe_info
    )

    st.write("### Analysis Plan")
    st.json(plan)
