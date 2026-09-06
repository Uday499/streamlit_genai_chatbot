from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO


# ---------------------------------------------------------
# Helper function
# ---------------------------------------------------------

def get_dataframe_info(df):
    return df.to_string(index=False)


# ---------------------------------------------------------
# Create Excel file
# ---------------------------------------------------------

def create_excel_file(df):

    excel_buffer = BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Data"
        )

    excel_buffer.seek(0)

    return excel_buffer


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

        # -------------------------------------------------
        # USER MESSAGE
        # -------------------------------------------------

        if message["role"] == "user":

            with st.chat_message("user"):
                st.markdown(message["content"])


        # -------------------------------------------------
        # NORMAL ASSISTANT MESSAGE
        # -------------------------------------------------

        elif message["role"] == "assistant":

            with st.chat_message("assistant"):
                st.markdown(message["content"])


        # -------------------------------------------------
        # CHART
        # -------------------------------------------------

        elif message["role"] == "chart":

            with st.chat_message("assistant"):

                chart_type = message["chart_type"]
                group_by = message["group_by"]
                metric = message["metric"]
                aggregation = message["aggregation"]


                # Create chart
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

                    st.error(
                        "Unsupported chart type."
                    )


                # Display chart + download button
                if fig is not None:

                    st.pyplot(fig)

                    # -----------------------------
                    # Download chart as PNG
                    # -----------------------------

                    image_buffer = BytesIO()

                    fig.savefig(
                        image_buffer,
                        format="png",
                        bbox_inches="tight"
                    )

                    image_buffer.seek(0)

                    st.download_button(
                        label="⬇️ Download Chart",
                        data=image_buffer,
                        file_name=f"{chart_type}_chart.png",
                        mime="image/png"
                    )

                    plt.close(fig)


        # -------------------------------------------------
        # TABLE
        # -------------------------------------------------

        elif message["role"] == "table":

            with st.chat_message("assistant"):

                columns = message["columns"]

                # If ALL columns were requested
                if columns == ["ALL"]:

                    table_df = df.copy()

                else:

                    # Check requested columns exist
                    valid_columns = [
                        column
                        for column in columns
                        if column in df.columns
                    ]

                    invalid_columns = [
                        column
                        for column in columns
                        if column not in df.columns
                    ]

                    if invalid_columns:

                        st.error(
                            f"Column(s) not found: {', '.join(invalid_columns)}"
                        )

                        continue

                    table_df = df[valid_columns].copy()


                # Display table
                st.dataframe(
                    table_df,
                    use_container_width=True
                )


                # -----------------------------
                # Create Excel file
                # -----------------------------

                excel_file = create_excel_file(
                    table_df
                )


                # -----------------------------
                # Download Excel button
                # -----------------------------

                st.download_button(
                    label="⬇️ Download Excel",
                    data=excel_file,
                    file_name="table.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )


    # -----------------------------------------------------
    # Initiate LLM
    # -----------------------------------------------------

    llm = ChatGroq(
        model="groq/compound-mini",
        temperature=0.0
    )


    # -----------------------------------------------------
    # User prompt
    # -----------------------------------------------------

    user_prompt = st.chat_input(
        "Ask Chatbot..."
    )


    if user_prompt:

        # -------------------------------------------------
        # Store user message
        # -------------------------------------------------

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_prompt
            }
        )


        # -------------------------------------------------
        # LLM prompt
        # -------------------------------------------------

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


If the user asks for a TABLE, respond with exactly this format:

TABLE_REQUEST
columns: <column1>, <column2>, <column3>


If the user asks for a table containing all columns, respond with:

TABLE_REQUEST
columns: ALL


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


User:
"Show me the Region and Total_Sales columns"

Response:
TABLE_REQUEST
columns: Region, Total_Sales


User:
"Show me the complete table"

Response:
TABLE_REQUEST
columns: ALL


If the user is not asking for a chart or table, answer normally in natural language.
"""


        # -------------------------------------------------
        # Get LLM response
        # -------------------------------------------------

        response = llm.invoke(prompt)

        assistant_response = response.content.strip()


        # -------------------------------------------------
        # CHART REQUEST
        # -------------------------------------------------

        if assistant_response.startswith(
            "CHART_REQUEST"
        ):

            lines = assistant_response.splitlines()

            chart_type = lines[1].split(
                ":",
                1
            )[1].strip()

            group_by = lines[2].split(
                ":",
                1
            )[1].strip()

            metric = lines[3].split(
                ":",
                1
            )[1].strip()

            aggregation = lines[4].split(
                ":",
                1
            )[1].strip()


            # Store chart in history

            st.session_state.chat_history.append(
                {
                    "role": "chart",
                    "chart_type": chart_type,
                    "group_by": group_by,
                    "metric": metric,
                    "aggregation": aggregation
                }
            )


        # -------------------------------------------------
        # TABLE REQUEST
        # -------------------------------------------------

        elif assistant_response.startswith(
            "TABLE_REQUEST"
        ):

            lines = assistant_response.splitlines()

            columns_text = lines[1].split(
                ":",
                1
            )[1].strip()


            if columns_text.upper() == "ALL":

                columns = ["ALL"]

            else:

                columns = [
                    column.strip()
                    for column in columns_text.split(",")
                ]


            # Store table in history

            st.session_state.chat_history.append(
                {
                    "role": "table",
                    "columns": columns
                }
            )


        # -------------------------------------------------
        # NORMAL ASSISTANT RESPONSE
        # -------------------------------------------------

        else:

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": assistant_response
                }
            )


        # -------------------------------------------------
        # Rerun
        # -------------------------------------------------

        st.rerun()
