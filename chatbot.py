from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq
import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------------------------------
# Helper function
# ---------------------------------------------------------

def get_dataframe_info(df):
    return df.to_string(index=False)


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# Streamlit page setup
# ---------------------------------------------------------

st.set_page_config(
    page_title="Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Generative AI Chatbot")


# ---------------------------------------------------------
# Upload CSV
# ---------------------------------------------------------

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


    # -----------------------------------------------------
    # Initiate chat history
    # -----------------------------------------------------

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


    # -----------------------------------------------------
    # Chart functions
    # -----------------------------------------------------

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
        ax.set_title(
            f"{aggregation.title()} of {metric} by {group_by}"
        )

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
        ax.set_title(
            f"{aggregation.title()} of {metric} by {group_by}"
        )

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
        ax.set_title(
            f"{aggregation.title()} of {metric} by {group_by}"
        )

        plt.tight_layout()

        return fig


    # -----------------------------------------------------
    # DISPLAY CHAT HISTORY
    # -----------------------------------------------------

    for message in st.session_state.chat_history:

        if message["role"] == "user":

            with st.chat_message("user"):
                st.markdown(message["content"])


        elif message["role"] == "assistant":

            with st.chat_message("assistant"):
                st.markdown(message["content"])


        elif message["role"] == "chart":

            with st.chat_message("assistant"):

                chart_type = message["chart_type"]
                group_by = message["group_by"]
                metric = message["metric"]
                aggregation = message["aggregation"]

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
                    fig = None
                    st.error("Unsupported chart type.")

                if fig is not None:
                    st.pyplot(fig)

                    plt.close(fig)


    # -----------------------------------------------------
    # LLM
    # -----------------------------------------------------

    llm = ChatGroq(
        model="groq/compound-mini",
        temperature=0.0
    )


    # -----------------------------------------------------
    # User prompt
    # -----------------------------------------------------

    user_prompt = st.chat_input("Ask Chatbot...")


    if user_prompt:

        # ---------------------------------------------
        # Store user message
        # ---------------------------------------------

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_prompt
            }
        )


        # ---------------------------------------------
        # LLM prompt
        # ---------------------------------------------

        prompt = f"""
You are a helpful data analysis assistant.

The user has uploaded the following CSV data:

{dataframe_info}

Previous conversation:
{st.session_state.chat_history}

Current user question:
{user_prompt}

Answer the user's question using the uploaded data.

If the user is asking for a normal question, answer normally in natural language.

If the user asks for a BAR CHART, respond with exactly this format:

CHART_REQUEST
chart_type: bar
group_by: <column name>
metric: <column name>
aggregation: <sum/mean/count>

If the user asks for a LINE CHART or asks to show a TREND, respond with exactly this format:

CHART_REQUEST
chart_type: line
group_by: <column name>
metric: <column name>
aggregation: <sum/mean/count>

If the user asks for a PIE CHART or asks to show a DISTRIBUTION, respond with exactly this format:

CHART_REQUEST
chart_type: pie
group_by: <column name>
metric: <column name>
aggregation: <sum/mean/count>

Examples:

User:
"Show total sales by region as a bar chart"

Response:
CHART_REQUEST
chart_type: bar
group_by: Region
metric: Total_Sales
aggregation: sum

User:
"Show average sales by region as a line chart"

Response:
CHART_REQUEST
chart_type: line
group_by: Region
metric: Total_Sales
aggregation: mean

User:
"Show the distribution of sales by region"

Response:
CHART_REQUEST
chart_type: pie
group_by: Region
metric: Total_Sales
aggregation: sum

If the user is not asking for a chart, answer normally in natural language.
"""


        # ---------------------------------------------
        # Get LLM response
        # ---------------------------------------------

        response = llm.invoke(prompt)

        assistant_response = response.content


        # ---------------------------------------------
        # Process response
        # ---------------------------------------------

        if assistant_response.startswith("CHART_REQUEST"):

            lines = assistant_response.splitlines()

            chart_type = lines[1].split(":", 1)[1].strip()
            group_by = lines[2].split(":", 1)[1].strip()
            metric = lines[3].split(":", 1)[1].strip()
            aggregation = lines[4].split(":", 1)[1].strip()


            # Store chart information
            st.session_state.chat_history.append(
                {
                    "role": "chart",
                    "chart_type": chart_type,
                    "group_by": group_by,
                    "metric": metric,
                    "aggregation": aggregation
                }
            )


        else:

            # Store normal assistant response
            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": assistant_response
                }
            )


        # ---------------------------------------------
        # Rerun so entire chat history is rendered
        # ---------------------------------------------

        st.rerun()
