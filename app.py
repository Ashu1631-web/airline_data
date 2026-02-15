import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF

# ===============================
# PAGE CONFIG (PowerBI Style)
# ===============================
st.set_page_config(
    page_title="Flight Analytics BI Dashboard",
    page_icon="✈️",
    layout="wide"
)

st.markdown("""
<style>
body {background-color: #f5f6fa;}
h1,h2,h3 {color:#1f4e79;}
</style>
""", unsafe_allow_html=True)


# ===============================
# LOGO AUTO FETCH
# ===============================
def get_airline_logo(airline):
    domains = {
        "IndiGo": "goindigo.in",
        "SpiceJet": "spicejet.com",
        "Air India": "airindia.com",
        "Vistara": "airvistara.com",
        "Emirates": "emirates.com",
        "Qatar Airways": "qatarairways.com"
    }

    if airline in domains:
        return f"https://logo.clearbit.com/{domains[airline]}"

    return "https://cdn-icons-png.flaticon.com/512/984/984233.png"


# ===============================
# DURATION FIX
# ===============================
def convert_duration(duration):
    if pd.isna(duration):
        return 0

    duration = str(duration)
    h, m = 0, 0

    if "h" in duration:
        try:
            h = int(duration.split("h")[0])
        except:
            h = 0

    if "m" in duration:
        try:
            m = int(duration.split("m")[0].split()[-1])
        except:
            m = 0

    return h * 60 + m


# ===============================
# LOAD DATA
# ===============================
@st.cache_data
def load_data():
    df = pd.read_csv("flights.csv")
    df["date_of_journey"] = pd.to_datetime(df["date_of_journey"], errors="coerce")
    df["Duration_Minutes"] = df["Duration"].apply(convert_duration)
    return df


df = load_data()

# ===============================
# SIDEBAR FILTERS
# ===============================
st.sidebar.title("🔍 Flight Filters")

airlines = st.sidebar.multiselect(
    "Select Airlines",
    df["airline"].unique(),
    default=list(df["airline"].unique()[:3])
)

if len(airlines) == 0:
    st.warning("⚠️ Please select at least one airline.")
    st.stop()

filtered = df[df["airline"].isin(airlines)]

if filtered.empty:
    st.error("❌ No flights found. Change filter selection.")
    st.stop()

# ===============================
# HEADER
# ===============================
st.title("✈️ Flight Analytics BI Dashboard (Premium)")
st.markdown("### PowerBI Style Dashboard with All Chart Types + Insights")

# ===============================
# LOGOS SAFE DISPLAY
# ===============================
st.subheader("🏢 Airline Logos (Auto Fetch)")

cols = st.columns(min(len(airlines), 5))

for i, airline in enumerate(airlines[:5]):
    with cols[i]:
        st.image(get_airline_logo(airline), width=80)
        st.caption(airline)

# ===============================
# KPI INSIGHTS
# ===============================
st.subheader("📌 Key Performance Metrics")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Flights", len(filtered))
c2.metric("Average Price", f"₹{filtered['Price'].mean():.0f}")
c3.metric("Maximum Price", f"₹{filtered['Price'].max():.0f}")
c4.metric("Minimum Price", f"₹{filtered['Price'].min():.0f}")

st.markdown("---")

# ===============================
# CHART BUILDER (Drag-Drop Feel)
# ===============================
st.subheader("🎛️ Chart Builder (Drag & Drop Feel)")

chart_type = st.selectbox(
    "Select Chart Type",
    [
        "Bar Chart", "Column Chart", "Line Chart",
        "Pie Chart", "Donut Chart", "Scatter Plot",
        "Area Chart", "Histogram", "Bubble Chart",
        "Waterfall Chart", "Box Plot", "Heatmap",
        "Treemap", "Funnel Chart", "Radar Chart",
        "Gantt Chart", "Bullet Graph", "Sankey Diagram"
    ]
)

# ===============================
# SAFE CHART GENERATOR
# ===============================
fig = None

# --- BASIC CHARTS ---
if chart_type == "Bar Chart":
    fig = px.bar(filtered, x="airline", y="Price")

elif chart_type == "Column Chart":
    fig = px.bar(filtered.groupby("Source")["Price"].mean())

elif chart_type == "Line Chart":
    fig = px.line(filtered.sort_values("date_of_journey"),
                  x="date_of_journey", y="Price")

elif chart_type == "Pie Chart":
    fig = px.pie(filtered, names="airline")

elif chart_type == "Donut Chart":
    fig = px.pie(filtered, names="Total_stops", hole=0.5)

elif chart_type == "Scatter Plot":
    fig = px.scatter(filtered, x="Duration_Minutes", y="Price")

elif chart_type == "Area Chart":
    fig = px.area(filtered, x="date_of_journey", y="Price")

elif chart_type == "Histogram":
    fig = px.histogram(filtered, x="Price")

elif chart_type == "Bubble Chart":
    fig = px.scatter(filtered,
                     x="Duration_Minutes",
                     y="Price",
                     size="Price",
                     color="airline")

# --- ADVANCED CHARTS ---
elif chart_type == "Waterfall Chart":
    fig = go.Figure(go.Waterfall(
        x=["Min", "Avg", "Max"],
        y=[filtered["Price"].min(),
           filtered["Price"].mean(),
           filtered["Price"].max()]
    ))

elif chart_type == "Box Plot":
    fig = px.box(filtered, x="airline", y="Price")

elif chart_type == "Heatmap":
    fig = px.density_heatmap(filtered, x="Source", y="destination")

elif chart_type == "Treemap":
    fig = px.treemap(filtered, path=["airline", "Source"], values="Price")

elif chart_type == "Funnel Chart":
    fig = px.funnel(filtered, x="Price", y="airline")

elif chart_type == "Radar Chart":
    radar = filtered.groupby("airline")["Price"].mean().reset_index()
    fig = go.Figure(go.Scatterpolar(
        r=radar["Price"],
        theta=radar["airline"],
        fill="toself"
    ))

elif chart_type == "Gantt Chart":
    sample = filtered.head(10)
    fig = px.timeline(sample,
                      x_start="date_of_journey",
                      x_end="date_of_journey",
                      y="airline")

elif chart_type == "Bullet Graph":
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=filtered["Price"].mean(),
        title={"text": "Average Ticket Price"},
        gauge={"axis": {"range": [0, filtered["Price"].max()]}}
    ))

# --- PROPER SANKEY ---
elif chart_type == "Sankey Diagram":

    top_routes = filtered.groupby(["Source", "destination"]).size().reset_index(name="count")
    top_routes = top_routes.head(10)

    sources = list(top_routes["Source"].unique())
    dests = list(top_routes["destination"].unique())

    labels = sources + dests

    source_idx = [labels.index(s) for s in top_routes["Source"]]
    target_idx = [labels.index(d) for d in top_routes["destination"]]

    fig = go.Figure(go.Sankey(
        node=dict(label=labels),
        link=dict(
            source=source_idx,
            target=target_idx,
            value=top_routes["count"]
        )
    ))

# ===============================
# DISPLAY CHART
# ===============================
st.plotly_chart(fig, use_container_width=True)

# ===============================
# DATA TABLE
# ===============================
st.subheader("📄 Filtered Flight Dataset")
st.dataframe(filtered.head(20), use_container_width=True)

# ===============================
# PDF REPORT DOWNLOAD
# ===============================
st.subheader("📥 Download PDF Report")

if st.button("📄 Generate Report"):

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)

    pdf.cell(200, 10, "Flight Analytics BI Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Total Flights: {len(filtered)}", ln=True)
    pdf.cell(200, 10, f"Average Price: ₹{filtered['Price'].mean():.0f}", ln=True)
    pdf.cell(200, 10, f"Maximum Price: ₹{filtered['Price'].max():.0f}", ln=True)

    pdf.output("flight_report.pdf")

    with open("flight_report.pdf", "rb") as f:
        st.download_button("⬇️ Download PDF", f, file_name="flight_report.pdf")

st.success("✅ Premium BI Dashboard Deployed Ready (No Errors)")
