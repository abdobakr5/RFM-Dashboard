
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ================== إعداد الصفحة ==================
st.set_page_config(page_title="RFM Dashboard", layout="wide")

# ================== تحميل البيانات ==================
rfm = pd.read_csv("rfm_analysis.csv")
rfm.drop(columns=['Unnamed: 0'], inplace=True)

df = pd.read_excel("__فرع الدمام السستيم_ (1).xlsx")
df.drop(columns=['#','Quotation No','Branch','From','Remark','Due Price'], inplace=True)
df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Day'] = df['Date'].dt.day
df['DayName'] = df['Date'].dt.day_name()

# ================== Sidebar Filters ==================
st.sidebar.header("Filters")
segment_filter = st.sidebar.multiselect(
    "Select Value Segment:",
    options=rfm["Segment"].unique(),
    default=rfm["Segment"].unique()
)

year_filter = st.sidebar.multiselect(
    "Select Year:",
    options=df["Year"].unique(),
    default=df["Year"].unique()
)

# ================== Helper Function for KPI Cards ==================
def kpi_card(title, value, color):
    st.markdown(
        f"""
        <div style="padding:15px; border-radius:12px; background-color:{color}; text-align:center; color:white;">
            <h4 style="margin:0; font-size:18px;">{title}</h4>
            <h2 style="margin:0; font-size:28px;">{value}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

# ================== KPI Cards ==================
st.title("📊 RFM & Sales Dashboard")

filtered_rfm = rfm[rfm["Segment"].isin(segment_filter)]

# صف أول: Averages
st.markdown("### 🔹 Averages")
col1, col2, col3 = st.columns(3)
with col1:
    kpi_card("Avg Recency (days)", round(filtered_rfm["Recency"].mean(), 1), "#3498db")
with col2:
    kpi_card("Avg Frequency", round(filtered_rfm["Frequency"].mean(), 1), "#27ae60")
with col3:
    kpi_card("Avg Monetary", round(filtered_rfm["Monetary"].mean(), 1), "#e67e22")

# صف ثاني: Totals
st.markdown("### 🔹 Totals")
col4, col5 = st.columns(2)
with col4:
    kpi_card("Total Frequency", int(filtered_rfm["Frequency"].sum()), "#9b59b6")
with col5:
    kpi_card("Total Monetary", round(filtered_rfm["Monetary"].sum(), 2), "#2c3e50")

# صف ثالث: Counts
st.markdown("### 🔹 Counts")
col6, col7, col8 = st.columns(3)
with col6:
    kpi_card("Count of Customers", filtered_rfm.shape[0], "#1abc9c")
with col7:
    kpi_card("Count of Transactions", int(filtered_rfm["Frequency"].sum()), "#f39c12")
with col8:
    kpi_card("Count of Segments", filtered_rfm["Segment"].nunique(), "#c0392b")

# ================== RFM Segment Distribution ==================
st.subheader("📌 Value Segment Distribution")
fig = px.histogram(
    filtered_rfm, 
    x="Segment", 
    color="Segment",
    text_auto=True,
    title="Customer Segments",
    category_orders={"Segment": filtered_rfm["Segment"].value_counts().index}
)
st.plotly_chart(fig, use_container_width=True)

# ================== Sales Data Analysis ==================
st.subheader("📌 Sales Data Analysis")

filtered_df = df[df["Year"].isin(year_filter)]

col1, col2 = st.columns(2)
with col1:
    st.write("### Status Distribution")
    fig1 = px.pie(filtered_df, names="Status", title="Status Distribution", 
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.write("### Type Distribution")
    type_counts = filtered_df["Type"].value_counts().reset_index()
    type_counts.columns = ["Type", "Count"]  # fix here
    fig2 = px.bar(type_counts,
                  x="Type", y="Count", text_auto=True,
                  labels={"Type":"Type", "Count":"Count"},
                  title="Type Distribution",
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig2, use_container_width=True)

st.write("### Average Net Price by Year/Month/Day/Status/Type")

metrics = {
    "Year": "Average by Year",
    "Month": "Average by Month",
    "DayName": "Average by DayName",
    "Day": "Average by Day",
    "Status": "Average by Status",
    "Type": "Average by Type"
}

for col, title in metrics.items():
    avg_df = filtered_df.groupby(col)['Net Price'].mean().reset_index()
    fig = px.bar(
        avg_df,
        x=col, y="Net Price", text_auto=".2f",
        title=title,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig, use_container_width=True)

# ================== RFM Table ==================
st.subheader("📌 RFM Table")
st.dataframe(filtered_rfm)
