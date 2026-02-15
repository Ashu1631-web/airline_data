import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

# ===============================
# CONFIG
# ===============================
st.set_page_config("Flight Analytics Ultra Premium", "✈️", layout="wide")

# ===============================
# LOAD DATA
# ===============================
@st.cache_data
def load_data():
    df = pd.read_csv("flights.csv")
    return df

df = load_data()

# ===============================
# FULL INDIAN AIRPORT COORDINATES
# ===============================
airport_coords = {
    "Delhi": [77.20, 28.61],
    "New Delhi": [77.20, 28.61],
    "Mumbai": [72.87, 19.07],
    "Kolkata": [88.36, 22.57],
    "Chennai": [80.27, 13.08],
    "Bangalore": [77.59, 12.97],
    "Hyderabad": [78.48, 17.38],
    "Cochin": [76.27, 9.93],
    "Goa": [73.83, 15.49],
    "Jaipur": [75.79, 26.91],
    "Lucknow": [80.95, 26.85],
    "Ahmedabad": [72.58, 23.03],
    "Pune": [73.85, 18.52],
}

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
# EMPTY STATE FIX (MP4 Video)
# ===============================
if len(airlines) == 0:
    st.title("✈️ Flight Analytics BI Dashboard")
    st.markdown("### Select an Airline from sidebar to start 🚀")

    # MP4 Flight Animation (Always Works)
    st.video("https://cdn.pixabay.com/vimeo/328940562/airplane-22165.mp4?width=640&hash=9f2b4e")

    # Quick Insights
    st.subheader("📌 Dataset Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Flights", len(df))
    c2.metric("Total Airlines", df["airline"].nunique())
    c3.metric("Average Price", f"₹{df['Price'].mean():.0f}")

    st.info("👈 Use filters to explore routes & pricing.")
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
    st.error("❌ No flights found. Change filters.")
    st.stop()

# ===============================
# HEADER
# ===============================
st.title("✈️ Flight Analytics Ultra Premium Dashboard")
st.markdown("### 3D Flight Routes Map + Markers + Insights")

# ===============================
# KPI METRICS
# ===============================
c1, c2, c3, c4 = st.columns(4)
c1.metric("Flights Found", len(filtered))
c2.metric("Avg Price", f"₹{filtered['Price'].mean():.0f}")
c3.metric("Max Price", f"₹{filtered['Price'].max():.0f}")
c4.metric("Min Price", f"₹{filtered['Price'].min():.0f}")

# ===============================
# BUILD ROUTES + MARKERS
# ===============================
routes = []
points = []

for _, row in filtered.head(25).iterrows():
    src = row["Source"]
    dst = row["destination"]

    if src in airport_coords and dst in airport_coords:
        s = airport_coords[src]
        d = airport_coords[dst]

        routes.append({
            "from_lon": s[0], "from_lat": s[1],
            "to_lon": d[0], "to_lat": d[1]
        })

        points.append({"lon": s[0], "lat": s[1], "city": src})
        points.append({"lon": d[0], "lat": d[1], "city": dst})

# ===============================
# 3D MAP WITH ARCS + MARKERS
# ===============================
st.subheader("🌍 3D Flight Route Map (Visible + Markers)")

arc_layer = pdk.Layer(
    "ArcLayer",
    data=routes,
    get_source_position=["from_lon", "from_lat"],
    get_target_position=["to_lon", "to_lat"],
    get_width=4,
    get_source_color=[0, 255, 0],
    get_target_color=[255, 0, 0],
    pickable=True,
    auto_highlight=True
)

point_layer = pdk.Layer(
    "ScatterplotLayer",
    data=points,
    get_position=["lon", "lat"],
    get_radius=50000,
    get_fill_color=[0, 0, 255],
    pickable=True
)

view_state = pdk.ViewState(
    latitude=22.5,
    longitude=78.9,
    zoom=4,
    pitch=50
)

st.pydeck_chart(pdk.Deck(
    layers=[arc_layer, point_layer],
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/light-v10"
))

# ===============================
# BASIC CHARTS
# ===============================
st.subheader("📊 Price Analytics")

st.plotly_chart(px.histogram(filtered, x="Price"), use_container_width=True)
st.plotly_chart(px.box(filtered, x="airline", y="Price"), use_container_width=True)

# ===============================
# TABLE
# ===============================
st.subheader("📄 Flight Data Preview")
st.dataframe(filtered.head(20), use_container_width=True)

st.success("✅ Final Ultra Premium Dashboard Ready 🚀")
