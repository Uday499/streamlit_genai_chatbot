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
    page_title="DataSense AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
<style>

.main-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 0px;
}

.subtitle {
    font-size: 18px;
    color: #6b7280;
    margin-top: 0px;
    margin-bottom: 25px;
}

.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-top: 10px;
    margin-bottom: 10px;
}

.metric-card {
    padding: 15px;
    border-radius: 10px;
    border: 1px solid rgba(128, 128, 128, 0.25);
    text-align: center;
}

.metric-value {
    font-size: 25px;
    font-weight: 700;
}

.metric-label {
    font-size: 14px;
    color: #6b7280;
}

.sidebar-title {
    font-size: 25px;
    font-weight: 700;
    margin-bottom: 5px;
}

.sidebar-subtitle {
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 20px;
}

.example-prompt {
    padding: 10px 12px;
    border-radius: 8px;
    border: 1px solid rgba(128, 128, 128, 0.2);
    margin-bottom: 8px;
    font-size: 14px;
}

</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "chat_history" not in st.session_state:

    st.session_state.chat_history = []


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-title">
            📊 DataSense AI
        </div>

        <div class="sidebar-subtitle">
            Your Conversational Data Analytics Assistant
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### 💡 What can I do?")

    st.markdown(
        """
        - 📊 Generate bar charts
        - 📈 Generate line charts
        - 🥧 Generate pie charts
        - 📋 Create summary tables
        - 📥 Download charts as PNG
        - 📥 Download tables as Excel
        - 💬 Ask questions using natural language
        """
    )

    st.divider()

    st.markdown("### ✨ Example prompts")

    st.markdown(
        """
        <div class="example-prompt">
        Show total sales by region as a bar chart.
        </div>

        <div class="example-prompt">
        Show average sales by region in a table.
        </div>

        <div class="example-prompt">
        Show sales distribution by region as a pie chart.
        </div>

        <div class="example-prompt">
        Which region has the highest sales?
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.chat_history = []

        st.rerun()


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown(
    """
    <div class="main-title">
        📊 DataSense AI
    </div>

    <div class="subtitle">
        Your Conversational Data Analytics Assistant
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    Upload a CSV file and ask questions about your data using
    natural language. Generate insights, visualizations and
    downloadable reports.
    """
)


# =========================================================
# UPLOAD CSV
# =========================================================

st.markdown(
    '<div class="section-title">📁 Upload your dataset</div>',
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"],
    help="Upload a CSV file to start analyzing your data."
)


# =========================================================
# ONLY CONTINUE IF FILE IS UPLOADED
# =========================================================

if uploaded_file is not None:

    # =====================================================
    # READ CSV
    # =====================================================

    df = pd.read_csv(uploaded_file)


    # =====================================================
    # SUCCESS MESSAGE
    # =====================================================

    st.success(
        f"✅ {uploaded_file.name} loaded successfully!"
    )


    # =====================================================
    # DATASET METRICS
    # =====================================================

    col1, col2, col3 = st.columns(3)


    with col1:

        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{len(df):,}</div>'
            f'<div class="metric-label">Rows</div>'
            f'</div>',
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{len(df.columns)}</div>'
            f'<div class="metric-label">Columns</div>'
            f'</div>',
            unsafe_allow_html=True
        )


    with col3:

        dataset_size = (
            df.memory_usage(deep=True).sum() / 1024
        )

        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{dataset_size:.1f} KB</div>'
            f'<div class="metric-label">Dataset Size</div>'
            f'</div>',
            unsafe_allow_html=True
        )


    st.markdown("")


    # =====================================================
    # DATASET PREVIEW
    # =====================================================

    with st.expander(
        "🔍 Dataset Preview",
        expanded=False
    ):

        st.dataframe(
            df,
            use_container_width=True,
            height=300
        )


    # =====================================================
    # DATASET INFORMATION
    # =====================================================

    dataframe_info = get_dataframe_info(df)


    with st.expander(
        "📋 Dataset Information",
        expanded=False
    ):

        st.code(
            dataframe_info,
            language="text"
        )


    st.divider()


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

                try:

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

                except Exception as e:

                    st.error(
                        f"Unable to create chart: {e}"
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

                try:

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

                except Exception as e:

                    st.error(
                        f"Unable to create table: {e}"
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
    # CHAT SECTION
    # =====================================================

    st.markdown(
        '<div class="section-title">💬 Ask DataSense</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Analyze your dataset using natural language."
    )


    # =====================================================
    # USER PROMPT
    # =====================================================

    user_prompt = st.chat_input(
        "Ask anything about your data..."
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

            # ---------------------------------------------
            # Extract parameters safely
            # ---------------------------------------------

            lines = [
                line.strip()
                for line in assistant_response.splitlines()
                if line.strip()
            ]


            chart_type = None
            group_by = None
            metric = None
            aggregation = None


            for line in lines:

                if line.lower().startswith(
                    "chart_type:"
                ):

                    chart_type = (
                        line.split(
                            ":",
                            1
                        )[1]
                        .strip()
                        .lower()
                    )


                elif line.lower().startswith(
                    "group_by:"
                ):

                    group_by = (
                        line.split(
                            ":",
                            1
                        )[1]
                        .strip()
                    )


                elif line.lower().startswith(
                    "metric:"
                ):

                    metric = (
                        line.split(
                            ":",
                            1
                        )[1]
                        .strip()
                    )


                elif line.lower().startswith(
                    "aggregation:"
                ):

                    aggregation = (
                        line.split(
                            ":",
                            1
                        )[1]
                        .strip()
                        .lower()
                    )


            # ---------------------------------------------
            # Validate extracted values
            # ---------------------------------------------

            if (
                chart_type
                and group_by
                and metric
                and aggregation
            ):

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

                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": (
                            "I couldn't understand the chart request. "
                            "Please try asking for a bar, line, or pie chart."
                        )
                    }
                )


        # =================================================
        # TABLE REQUEST
        # =================================================

        elif assistant_response.startswith(
            "TABLE_REQUEST"
        ):

            # ---------------------------------------------
            # Extract parameters safely
            # ---------------------------------------------

            lines = [
                line.strip()
                for line in assistant_response.splitlines()
                if line.strip()
            ]


            group_by = None
            metric = None
            aggregation = None


            for line in lines:

                if line.lower().startswith(
                    "group_by:"
                ):

                    group_by = (
                        line.split(
                            ":",
                            1
                        )[1]
                        .strip()
                    )


                elif line.lower().startswith(
                    "metric:"
                ):

                    metric = (
                        line.split(
                            ":",
                            1
                        )[1]
                        .strip()
                    )


                elif line.lower().startswith(
                    "aggregation:"
                ):

                    aggregation = (
                        line.split(
                            ":",
                            1
                        )[1]
                        .strip()
                        .lower()
                    )


            # ---------------------------------------------
            # Validate extracted values
            # ---------------------------------------------

            if (
                group_by
                and metric
                and aggregation
            ):

                st.session_state.chat_history.append(
                    {
                        "role": "table",
                        "group_by": group_by,
                        "metric": metric,
                        "aggregation": aggregation
                    }
                )

            else:

                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": (
                            "I couldn't understand the table request. "
                            "Please try asking for a table again."
                        )
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
