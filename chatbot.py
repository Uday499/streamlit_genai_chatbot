from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq
import pandas as pd
import json

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

def get_dataframe_info(df):
    info = []

    for column in df.columns:
        info.append(
            f"{column}: {df[column].dtype}"
        )

    return "\n".join(info)


def create_analysis_plan(llm, user_question, dataframe_info):

    prompt = f"""
You are a data analysis planner.

The user has uploaded a CSV dataset.

Dataset columns and data types:

{dataframe_info}

User question:

{user_question}

Determine the analysis required.

Return ONLY valid JSON.

Allowed operations:
- groupby
- trend
- top_n
- summary

Allowed aggregations:
- sum
- mean
- count
- min
- max

Allowed visualizations:
- bar
- line
- table

JSON format:

{{
    "operation": "...",
    "group_by": "...",
    "metric": "...",
    "aggregation": "...",
    "visualization": "...",
    "top_n": null
}}

If top_n is not required, use null.
"""

    response = llm.invoke(prompt)

    return json.loads(response.content)

df = None

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.success(
        f"Loaded {len(df):,} rows and {len(df.columns)} columns"
    )

    st.dataframe(df.head(10))

 dataframe_info = get_dataframe_info(df)

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
    plan = create_analysis_plan(
    llm,
    user_prompt,
    dataframe_info
)

st.write("Analysis plan:")
st.json(plan)
    st.chat_message("user").markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    response = llm.invoke(
        input = [{"role": "system", "content": "You are a helpful assistant"}, *st.session_state.chat_history]
    )
    assistant_response = response.content
    st.session_state.chat_history.append({"role": "system", "content": assistant_response})

    with st.chat_message("assistant"):
        st.markdown(assistant_response)
