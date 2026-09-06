from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq
import pandas as pd
import matplotlib.pyplot as plt

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

def create_bar_chart(df, group_by, metric, aggregation):

    if aggregation == "sum":
        result = df.groupby(group_by)[metric].sum()

    elif aggregation == "mean":
        result = df.groupby(group_by)[metric].mean()

    elif aggregation == "count":
        result = df.groupby(group_by)[metric].count()

    else:
        raise ValueError("Unsupported aggregation")

    fig, ax = plt.subplots()

    result.plot(
        kind="bar",
        ax=ax
    )

    ax.set_xlabel(group_by)
    ax.set_ylabel(metric)
    ax.set_title(f"{aggregation.title()} of {metric} by {group_by}")

    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig

def create_line_chart(df, group_by, metric, aggregation):

    if aggregation == "sum":
        result = df.groupby(group_by)[metric].sum()

    elif aggregation == "mean":
        result = df.groupby(group_by)[metric].mean()

    elif aggregation == "count":
        result = df.groupby(group_by)[metric].count()

    else:
        raise ValueError("Unsupported aggregation")

    fig, ax = plt.subplots()

    result.plot(
        kind="line",
        marker="o",
        ax=ax
    )

    ax.set_xlabel(group_by)
    ax.set_ylabel(metric)
    ax.set_title(f"{aggregation.title()} of {metric} by {group_by}")

    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig

def create_pie_chart(df, group_by, metric, aggregation):

    if aggregation == "sum":
        result = df.groupby(group_by)[metric].sum()

    elif aggregation == "mean":
        result = df.groupby(group_by)[metric].mean()

    elif aggregation == "count":
        result = df.groupby(group_by)[metric].count()

    else:
        raise ValueError("Unsupported aggregation")

    fig, ax = plt.subplots()

    result.plot(
        kind="pie",
        autopct="%1.1f%%",
        ax=ax
    )

    ax.set_ylabel("")
    ax.set_title(f"{aggregation.title()} of {metric} by {group_by}")

    plt.tight_layout()

    return fig

# creates user prompt on the UI
user_prompt = st.chat_input("Ask Chatbot...")

if user_prompt:

    st.chat_message("user").markdown(user_prompt)

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )

    prompt = f"""
You are a helpful data analysis assistant.

The user has uploaded the following CSV data:

{dataframe_info}

Previous conversation:
{st.session_state.chat_history}

Current user question:
{user_prompt}

Answer the user's question using the uploaded data.

If the user is asking for a normal answer, respond normally.

If the user asks for a BAR CHART, respond with exactly this format:

CHART_REQUEST
group_by: <column name>
metric: <column name>
aggregation: <sum/mean/count>

Do not calculate or describe the chart when using CHART_REQUEST.

For example, if the user asks:
"Show total sales by region as a bar chart"

respond:

CHART_REQUEST
group_by: Region
metric: Total_Sales
aggregation: sum

If the user is not asking for a bar chart, answer normally in natural language.
"""

    response = llm.invoke(prompt)

    assistant_response = response.content

    with st.chat_message("assistant"):

        if assistant_response.startswith("CHART_REQUEST"):

            lines = assistant_response.splitlines()

            chart_type = lines[1].split(":", 1)[1].strip()
            group_by = lines[2].split(":", 1)[1].strip()
            metric = lines[3].split(":", 1)[1].strip()
            aggregation = lines[4].split(":", 1)[1].strip()

            if chart_type == "bar":

                fig = create_bar_chart(
                    df,
                    group_by,
                    metric,
                    aggregation
                )

            elif chart_type == "line":

                fig = create_line_chart(
                    df,
                    group_by,
                    metric,
                    aggregation
                )

            elif chart_type == "pie":

                fig = create_pie_chart(
                    df,
                    group_by,
                    metric,
                    aggregation
                )

            else:

                st.error("Unsupported chart type.")
                fig = None

            if fig is not None:
                st.pyplot(fig)

                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": f"Displayed a {chart_type} chart of {metric} by {group_by}."
                    }
                )

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": f"Displayed a bar chart of {metric} by {group_by}."
                }
            )

        else:

            st.markdown(assistant_response)

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": assistant_response
                }
            )
