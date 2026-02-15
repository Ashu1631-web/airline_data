import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from fpdf import FPDF

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config("Flight Analytics BI Dashboard", "✈️", layout="wide")

# ===============================
# LOGO FETCHER (AUTO)
# ===============================
def get_airline_logo(airline):
    """
    Auto fetch airline logo using Clearbit API.
    If not found, show default plane icon.
    """

    domains = {
        "IndiGo": "goindigo.in",
        "SpiceJet": "spicejet.com",
        "Air India": "airindia.com",
        "Vistara": "airvistara.com",
        "GoAir": "goair.in",
        "Emirates": "emirates.com",
        "Qatar Airways": "qatarairways.com"
    }

    if airline in domains:
        return f"https://logo.clearbit.com/{domains[airline]}"

    # Default logo
    return "https://cdn-icons-png.flaticon.com/512/984/984233.png"


# ===============================
# DURATION FIX
# ===============================
def convert_duration_to_minutes(duration):
    if pd.isna(duration):
        return 0

    duration = str(duration)
    h, m = 0, 0

    if "h" in duration:
        h = int(duration.split("h")[0])

    if "m" in duration:
        m = int(duration.split("m")[0].split()[-1])

    return h * 60 + m


# ===============================
# LOAD DATA
# ===============================
@st.cache_data
def load_data():
    df = pd.read_csv("flights.csv")
    df["date_of_journey"] = pd.to_datetime(df["date_of_journey"], errors="coerce")
    df["Duration_Minutes"] = df["Duration"].apply(convert_duration_to_minutes)
    return df


df = load_data()

# ===============================
# SIDEBAR FILTERS
# ===============================
st.sidebar.title("🔍 Filters")

airlines = st.sidebar.multiselect(
    "Select Airlines",
    df["airline"].unique(),
    default=df["airline"].unique()[:4]
)

filtered = df[df["airline"].isin(airlines)]

# ===============================
# HEADER
# ===============================
st.title("✈️ Flight Analytics BI Dashboard (Premium)")
st.markdown("### Complete Business Intelligence Dashboard with All Chart Types")

# ===============================
# SHOW LOGOS AUTO
# ===============================
st.subheader("🏢 Airline Logos (Auto-Fetch)")

cols = st.columns(len(airlines))

for i, airline in enumerate(airlines):
    with cols[i]:
        st.image(get_airline_logo(airline), width=80)
        st.caption(airline)

# ===============================
# KPI METRICS
# ===============================
st.subheader("📌 Key Insights")

c1, c2, c3 = st.columns(3)
c1.metric("Total Flights", len(filtered))
c2.metric("Average Price", f"₹{filtered['Price'].mean():.0f}")
c3.metric("Max Price", f"₹{filtered['Price'].max():.0f}")

st.markdown("---")

# ===============================
# ALL CHART TYPES SECTION
# ===============================
st.subheader("📊 Complete Chart Gallery")

charts = {}

# 1 Bar Chart
charts["Bar Chart"] = px.bar(filtered, x="airline", y="Price")

# 2 Column Chart
charts["Column Chart"] = px.bar(filtered.groupby("Source")["Price"].mean())

# 3 Line Chart
charts["Line Chart"] = px.line(filtered.sort_values("date_of_journey"),
                               x="date_of_journey", y="Price")

# 4 Pie Chart
charts["Pie Chart"] = px.pie(filtered, names="airline")

# 5 Donut Chart
charts["Donut Chart"] = px.pie(filtered, names="Total_stops", hole=0.5)

# 6 Scatter Plot
charts["Scatter Plot"] = px.scatter(filtered, x="Duration_Minutes", y="Price")

# 7 Area Chart
charts["Area Chart"] = px.area(filtered, x="date_of_journey", y="Price")

# 8 Histogram
charts["Histogram"] = px.histogram(filtered, x="Price")

# 9 Bubble Chart
charts["Bubble Chart"] = px.scatter(filtered,
                                    x="Duration_Minutes",
                                    y="Price",
                                    size="Price",
                                    color="airline")

# 10 Waterfall Chart
charts["Waterfall Chart"] = go.Figure(go.Waterfall(
    x=["Min", "Avg", "Max"],
    y=[filtered["Price"].min(),
       filtered["Price"].mean(),
       filtered["Price"].max()]
))

# 11 Box Plot
charts["Box Plot"] = px.box(filtered, x="airline", y="Price")

# 12 Heatmap
charts["Heatmap"] = px.density_heatmap(filtered, x="Source", y="destination")

# 13 Treemap
charts["Treemap"] = px.treemap(filtered, path=["airline", "Source"], values="Price")

# 14 Funnel Chart
charts["Funnel Chart"] = px.funnel(filtered, x="Price", y="airline")

# 15 Radar Chart
radar = filtered.groupby("airline")["Price"].mean().reset_index()
charts["Radar Chart"] = go.Figure(
    go.Scatterpolar(
        r=radar["Price"],
        theta=radar["airline"],
        fill="toself"
    )
)

# 16 Gantt Chart (Dummy Example)
gantt = filtered.head(10)
charts["Gantt Chart"] = px.timeline(
    gantt,
    x_start="date_of_journey",
    x_end="date_of_journey",
    y="airline"
)

# 17 Bullet Graph
charts["Bullet Graph"] = go.Figure(go.Indicator(
    mode="gauge+number",
    value=filtered["Price"].mean(),
    title={"text": "Average Price Gauge"},
    gauge={"axis": {"range": [0, filtered["Price"].max()]}}
))

# 18 Sankey Diagram
charts["Sankey Diagram"] = go.Figure(go.Sankey(
    node=dict(label=list(filtered["Source"].unique()) + list(filtered["destination"].unique())),
    link=dict(
        source=[0]*len(filtered),
        target=[1]*len(filtered),
        value=filtered["Price"]
    )
))

# ===============================
# CHART SELECTOR
# ===============================
selected = st.selectbox("📌 Select Any Chart Type", list(charts.keys()))

st.plotly_chart(charts[selected], use_container_width=True)

# ===============================
# PDF DOWNLOAD
# ===============================
if st.button("📄 Generate PDF Report"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, "Flight Analytics BI Report", ln=True, align="C")
    pdf.output("report.pdf")

    with open("report.pdf", "rb") as f:
        st.download_button("⬇️ Download Report PDF", f, file_name="report.pdf")

st.success("✅ Premium BI Dashboard Ready (All Graph Types Included)")
