import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import requests

# ===============================
# CONFIG
# ===============================
st.set_page_config(
    page_title="Flight Analytics Ultra Premium",
    page_icon="✈️",
    layout="wide"
)

# ===============================
# LOAD DATA
# ===============================
@st.cache_data
def load_data():
    df = pd.read_csv("flights.csv")
    df["date_of_journey"] = pd.to_datetime(df["date_of_journey"], errors="coerce")
    return df

df = load_data()

# ===============================
# SIDEBAR FILTERS
# ===============================
st.sidebar.title("🔍 Flight Filters")

airlines = st.sidebar.multiselect(
    "Select Airline",
    df["airline"].unique(),
    default=[]
)

sources = st.sidebar.multiselect(
    "Select Source City",
    df["Source"].unique(),
    default=[]
)

destinations = st.sidebar.multiselect(
    "Select Destination City",
    df["destination"].unique(),
    default=[]
)

# ===============================
# EMPTY SCREEN (Video + Insights)
# ===============================
if len(airlines) == 0:
    st.title("✈️ Flight Analytics BI Dashboard")
    st.markdown("### Please select an airline from sidebar to explore insights 🚀")

    # Flight Video Animation
    st.video("https://www.youtube.com/watch?v=21X5lGlDOfg")

    # Dataset Insights
    st.subheader("📌 Dataset Quick Insights")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Flights", len(df))
    c2.metric("Total Airlines", df["airline"].nunique())
    c3.metric("Average Price", f"₹{df['Price'].mean():.0f}")

    st.info("👈 Select Airline + Cities from sidebar filters.")
    st.stop()

# ===============================
# APPLY FILTERS
# ===============================
filtered = df[df["airline"].isin(airlines)]

if sources:
    filtered = filtered[filtered["Source"].isin(sources)]

if destinations:
    filtered = filtered[filtered["destination"].isin(destinations)]

if filtered.empty:
    st.error("❌ No flights found. Please change filters.")
    st.stop()

# ===============================
# HEADER
# ===============================
st.title("✈️ Flight Analytics Ultra Premium Dashboard")
st.markdown("### PowerBI Style Dashboard with 3D Flight Routes Map")

# ===============================
# KPI METRICS
# ===============================
st.subheader("📌 Key Insights")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Flights Found", len(filtered))
c2.metric("Avg Price", f"₹{filtered['Price'].mean():.0f}")
c3.metric("Max Price", f"₹{filtered['Price'].max():.0f}")
c4.metric("Min Price", f"₹{filtered['Price'].min():.0f}")

# ===============================
# 3D FLIGHT ROUTE MAP
# ===============================
st.subheader("🌍 3D Flight Route Map (Source → Destination)")

city_coords = {
    "Delhi": [77.20, 28.61],
    "Mumbai": [72.87, 19.07],
    "Kolkata": [88.36, 22.57],
    "Chennai": [80.27, 13.08],
    "Bangalore": [77.59, 12.97],
    "Hyderabad": [78.48, 17.38],
}

routes = []

for _, row in filtered.head(25).iterrows():
    src = row["Source"]
    dst = row["destination"]

    if src in city_coords and dst in city_coords:
        routes.append({
            "start": city_coords[src],
            "end": city_coords[dst]
        })

if len(routes) == 0:
    st.warning("⚠️ No coordinate routes available for selected cities.")
else:
    arc_layer = pdk.Layer(
        "ArcLayer",
        data=routes,
        get_source_position="start",
        get_target_position="end",
        get_width=3,
        pickable=True
    )

    view_state = pdk.ViewState(
        latitude=22.5,
        longitude=78.9,
        zoom=3,
        pitch=45
    )

    st.pydeck_chart(pdk.Deck(
        layers=[arc_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v9"
    ))

# ===============================
# CHART DASHBOARD BUILDER
# ===============================
st.subheader("📊 Chart Dashboard Builder")

chart_options = st.multiselect(
    "Select Charts to Display",
    ["Price Distribution", "Airline Comparison", "Stops Pie", "Top Routes", "Price Trend"],
    default=["Price Distribution", "Airline Comparison"]
)

col1, col2 = st.columns(2)

with col1:
    if "Price Distribution" in chart_options:
        st.plotly_chart(px.histogram(filtered, x="Price"), use_container_width=True)

    if "Stops Pie" in chart_options:
        st.plotly_chart(px.pie(filtered, names="Total_stops"), use_container_width=True)

with col2:
    if "Airline Comparison" in chart_options:
        st.plotly_chart(px.box(filtered, x="airline", y="Price"), use_container_width=True)

    if "Top Routes" in chart_options:
        st.plotly_chart(px.bar(filtered["route"].value_counts().head(10)),
                        use_container_width=True)

if "Price Trend" in chart_options:
    st.plotly_chart(px.line(filtered, x="date_of_journey", y="Price"),
                    use_container_width=True)

# ===============================
# DATA TABLE
# ===============================
st.subheader("📄 Flight Dataset Preview")
st.dataframe(filtered.head(30), use_container_width=True)

st.success("✅ Ultra Premium Dashboard Ready for Streamlit Cloud 🚀")
