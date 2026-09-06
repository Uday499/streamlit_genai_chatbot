from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_dataframe_info(df):
    return df.to_string(index=False)


# =========================================================
# CREATE EXCEL FILE
# =========================================================

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


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# STREAMLIT PAGE SETUP
# =========================================================

st.set_page_config(
    page_title="Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Generative AI Chatbot")


# =========================================================
# UPLOAD CSV
# =========================================================

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


    # =====================================================
    # INITIATE CHAT HISTORY
    # =====================================================

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


    # =====================================================
    # CHART FUNCTIONS
    # =====================================================

    def create_bar_chart(
        df,
        group_by,
        metric,
        aggregation
    ):

        if aggregation == "sum":

            result = (
                df.groupby(group_by)[metric]
                .sum()
            )

        elif aggregation == "mean":

            result = (
                df.groupby(group_by)[metric]
                .mean()
            )

        elif aggregation == "count":

            result = (
                df.groupby(group_by)[metric]
                .count()
            )

        else:

            raise ValueError(
                "Unsupported aggregation"
            )


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

        plt.xticks(
            rotation=45
        )

        plt.tight_layout()

        return fig


    def create_line_chart(
        df,
        group_by,
        metric,
        aggregation
    ):

        if aggregation == "sum":

            result = (
                df.groupby(group_by)[metric]
                .sum()
            )

        elif aggregation == "mean":

            result = (
                df.groupby(group_by)[metric]
                .mean()
            )

        elif aggregation == "count":

            result = (
                df.groupby(group_by)[metric]
                .count()
            )

        else:

            raise ValueError(
                "Unsupported aggregation"
            )


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

        plt.xticks(
            rotation=45
        )

        plt.tight_layout()

        return fig


    def create_pie_chart(
        df,
        group_by,
        metric,
        aggregation
    ):

        if aggregation == "sum":

            result = (
                df.groupby(group_by)[metric]
                .sum()
            )

        elif aggregation == "mean":

            result = (
                df.groupby(group_by)[metric]
                .mean()
            )

        elif aggregation == "count":

            result = (
                df.groupby(group_by)[metric]
                .count()
            )

        else:

            raise ValueError(
                "Unsupported aggregation"
            )


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


    # =====================================================
    # DISPLAY CHAT HISTORY
    # =====================================================

    for message in st.session_state.chat_history:


        # =================================================
        # USER MESSAGE
        # =================================================

        if message["role"] == "user":

            with st.chat_message("user"):

                st.markdown(
                    message["content"]
                )


        # =================================================
        # NORMAL ASSISTANT RESPONSE
        # =================================================

        elif message["role"] == "assistant":

            with st.chat_message("assistant"):

                st.markdown(
                    message["content"]
                )


        # =================================================
        # CHART
        # =================================================

        elif message["role"] == "chart":

            with st.chat_message("assistant"):

                chart_type = message["chart_type"]

                group_by = message["group_by"]

                metric = message["metric"]

                aggregation = message["aggregation"]


                # -----------------------------------------
                # Validate columns
                # -----------------------------------------

                if group_by not in df.columns:

                    st.error(
                        f"Column '{group_by}' was not found in the dataset."
                    )

                    continue


                if metric not in df.columns:

                    st.error(
                        f"Column '{metric}' was not found in the dataset."
                    )

                    continue


                # -----------------------------------------
                # Create chart
                # -----------------------------------------

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

                    st.error(
                        "Unsupported chart type."
                    )

                    fig = None


                # -----------------------------------------
                # Display chart
                # -----------------------------------------

                if fig is not None:

                    st.pyplot(fig)


                    # -------------------------------------
                    # Create PNG
                    # -------------------------------------

                    image_buffer = BytesIO()

                    fig.savefig(
                        image_buffer,
                        format="png",
                        bbox_inches="tight"
                    )

                    image_buffer.seek(0)


                    # -------------------------------------
                    # Download chart
                    # -------------------------------------

                    st.download_button(
                        label="⬇️ Download Chart",
                        data=image_buffer,
                        file_name=(
                            f"{chart_type}_"
                            f"{metric}_by_"
                            f"{group_by}.png"
                        ),
                        mime="image/png"
                    )


                    plt.close(fig)


        # =================================================
        # TABLE
        # =================================================

        elif message["role"] == "table":

            with st.chat_message("assistant"):

                group_by = message["group_by"]

                metric = message["metric"]

                aggregation = message["aggregation"]


                # -----------------------------------------
                # Validate columns
                # -----------------------------------------

                if group_by not in df.columns:

                    st.error(
                        f"Column '{group_by}' was not found in the dataset."
                    )

                    continue


                if metric not in df.columns:

                    st.error(
                        f"Column '{metric}' was not found in the dataset."
                    )

                    continue


                # -----------------------------------------
                # Calculate table
                # -----------------------------------------

                if aggregation == "sum":

                    table_df = (
                        df.groupby(group_by)[metric]
                        .sum()
                        .reset_index()
                    )


                elif aggregation == "mean":

                    table_df = (
                        df.groupby(group_by)[metric]
                        .mean()
                        .reset_index()
                    )


                elif aggregation == "count":

                    table_df = (
                        df.groupby(group_by)[metric]
                        .count()
                        .reset_index()
                    )


                else:

                    st.error(
                        f"Unsupported aggregation: {aggregation}"
                    )

                    continue


                # -----------------------------------------
                # Rename metric column
                # -----------------------------------------

                table_df.columns = [
                    group_by,
                    f"{aggregation.title()} of {metric}"
                ]


                # -----------------------------------------
                # Display table
                # -----------------------------------------

                st.dataframe(
                    table_df,
                    use_container_width=True
                )


                # -----------------------------------------
                # Create Excel
                # -----------------------------------------

                excel_file = create_excel_file(
                    table_df
                )


                # -----------------------------------------
                # Download Excel
                # -----------------------------------------

                st.download_button(
                    label="⬇️ Download Excel",
                    data=excel_file,
                    file_name=(
                        f"{aggregation}_"
                        f"{metric}_by_"
                        f"{group_by}.xlsx"
                    ),
                    mime=(
                        "application/"
                        "vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    )
                )


    # =====================================================
    # INITIALIZE LLM
    # =====================================================

    llm = ChatGroq(
        model="groq/compound-mini",
        temperature=0.0
    )


    # =====================================================
    # USER PROMPT
    # =====================================================

    user_prompt = st.chat_input(
        "Ask Chatbot..."
    )


    if user_prompt:


        # =================================================
        # STORE USER MESSAGE
        # =================================================

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_prompt
            }
        )


        # =================================================
        # LLM PROMPT
        # =================================================

        prompt = f"""
You are a helpful data analysis assistant.

The user has uploaded the following CSV data:

{dataframe_info}


Previous conversation:

{st.session_state.chat_history}


Current user question:

{user_prompt}


Answer the user's question using the uploaded data.


=========================================================
CHART REQUESTS
=========================================================

If the user asks for a BAR CHART, respond with exactly:

CHART_REQUEST
chart_type: bar
group_by: <column name>
metric: <column name>
aggregation: <sum/mean/count>


If the user asks for a LINE CHART or asks to show a TREND, respond with exactly:

CHART_REQUEST
chart_type: line
group_by: <column name>
metric: <column name>
aggregation: <sum/mean/count>


If the user asks for a PIE CHART or asks to show a DISTRIBUTION, respond with exactly:

CHART_REQUEST
chart_type: pie
group_by: <column name>
metric: <column name>
aggregation: <sum/mean/count>


=========================================================
TABLE REQUESTS
=========================================================

If the user asks for a TABLE, respond with exactly:

TABLE_REQUEST
group_by: <column name>
metric: <column name>
aggregation: <sum/mean/count>


IMPORTANT:

NEVER return a Markdown table.

NEVER calculate or write the table values yourself.

Only return TABLE_REQUEST followed by group_by, metric and aggregation.

The Python application will calculate the table using the original CSV data.


Treat the following types of requests as TABLE_REQUEST when appropriate:

- breakdown
- summary
- grouped data
- data by category
- sales by region
- sales breakdown by region
- show each region
- summarize sales
- show a breakdown
- show a distribution in a table
- show values by category


Examples:


User:
"Show breakdown of sales by region"

Response:

TABLE_REQUEST
group_by: Region
metric: Total_Sales
aggregation: sum


User:
"Show average sales by region in a table"

Response:

TABLE_REQUEST
group_by: Region
metric: Total_Sales
aggregation: mean


User:
"Show number of sales by region"

Response:

TABLE_REQUEST
group_by: Region
metric: Total_Sales
aggregation: count


User:
"Give me a sales summary by region"

Response:

TABLE_REQUEST
group_by: Region
metric: Total_Sales
aggregation: sum


=========================================================
NORMAL QUESTIONS
=========================================================

If the user is not asking for a chart or a table,
answer normally in natural language.


IMPORTANT:

When returning CHART_REQUEST or TABLE_REQUEST,
do not include any additional explanation or Markdown.
"""


        # =================================================
        # GET LLM RESPONSE
        # =================================================

        response = llm.invoke(prompt)

        assistant_response = response.content.strip()


        # =================================================
        # CHART REQUEST
        # =================================================

        if assistant_response.startswith(
            "CHART_REQUEST"
        ):

            lines = assistant_response.splitlines()


            chart_type = (
                lines[1]
                .split(":", 1)[1]
                .strip()
            )


            group_by = (
                lines[2]
                .split(":", 1)[1]
                .strip()
            )


            metric = (
                lines[3]
                .split(":", 1)[1]
                .strip()
            )


            aggregation = (
                lines[4]
                .split(":", 1)[1]
                .strip()
            )


            # ---------------------------------------------
            # Store chart request
            # ---------------------------------------------

            st.session_state.chat_history.append(
                {
                    "role": "chart",
                    "chart_type": chart_type,
                    "group_by": group_by,
                    "metric": metric,
                    "aggregation": aggregation
                }
            )


        # =================================================
        # TABLE REQUEST
        # =================================================

        elif assistant_response.startswith(
            "TABLE_REQUEST"
        ):

            lines = assistant_response.splitlines()


            group_by = (
                lines[1]
                .split(":", 1)[1]
                .strip()
            )


            metric = (
                lines[2]
                .split(":", 1)[1]
                .strip()
            )


            aggregation = (
                lines[3]
                .split(":", 1)[1]
                .strip()
            )


            # ---------------------------------------------
            # Store table request
            # ---------------------------------------------

            st.session_state.chat_history.append(
                {
                    "role": "table",
                    "group_by": group_by,
                    "metric": metric,
                    "aggregation": aggregation
                }
            )


        # =================================================
        # NORMAL ASSISTANT RESPONSE
        # =================================================

        else:

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": assistant_response
                }
            )


        # =================================================
        # RERUN
        # =================================================

        st.rerun()
