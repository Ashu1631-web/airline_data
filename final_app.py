# Final app.py (Flight Analytics Portfolio Dashboard with Auto Coordinates)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Flight Analytics Portfolio Dashboard",
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
# AUTO COORDINATES FETCHER
# ===============================
@st.cache_data
def get_coordinates(city):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={city},India"
    try:
        response = requests.get(url, headers={"User-Agent": "flight-dashboard"})
        data = response.json()
        if len(data) > 0:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
    except:
        return None
    return None

# ===============================
# SIDEBAR FILTERS
# ===============================
st.sidebar.title("🔍 Flight Filters")

airlines = st.sidebar.multiselect("Select Airline", df["airline"].unique(), default=[])
sources = st.sidebar.multiselect("Select Source City", df["Source"].unique(), default=[])
destinations = st.sidebar.multiselect("Select Destination City", df["destination"].unique(), default=[])

# ===============================
# EMPTY STATE
# ===============================
if len(airlines) == 0:
    st.title("✈️ Flight Analytics Dashboard")
    st.markdown("### Please select an Airline from sidebar to explore insights 🚀")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Flights", len(df))
    c2.metric("Total Airlines", df["airline"].nunique())
    c3.metric("Average Price", f"₹{df['Price'].mean():.0f}")
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
st.title("✈️ Flight Analytics Portfolio Dashboard")
st.markdown("### Professional Flight Price + Route + Airline Insights")

# ===============================
# KPI METRICS
# ===============================
st.subheader("📌 Key Insights")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Flights Found", len(filtered))
c2.metric("Avg Price", f"₹{filtered['Price'].mean():.0f}")
c3.metric("Max Price", f"₹{filtered['Price'].max():.0f}")
c4.metric("Min Price", f"₹{filtered['Price'].min():.0f}")

st.markdown("---")

# ===============================
# ROUTE MAP (AUTO COORDINATES)
# ===============================
st.subheader("🗺️ Flight Route Map (Source → Destination)")

sample = filtered.iloc[0]
src = sample["Source"]
dst = sample["destination"]

src_coord = get_coordinates(src)
dst_coord = get_coordinates(dst)

if src_coord and dst_coord:

    src_lat, src_lon = src_coord
    dst_lat, dst_lon = dst_coord

    map_data = pd.DataFrame({
        "City": [src, dst],
        "lat": [src_lat, dst_lat],
        "lon": [src_lon, dst_lon],
        "Type": ["Source", "Destination"]
    })

    fig_map = px.scatter_mapbox(
        map_data,
        lat="lat",
        lon="lon",
        color="Type",
        zoom=4,
        hover_name="City"
    )

    fig_map.add_trace(
        go.Scattermapbox(
            mode="lines",
            lat=[src_lat, dst_lat],
            lon=[src_lon, dst_lon],
            line=dict(width=3),
            name="Route"
        )
    )

    fig_map.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    st.plotly_chart(fig_map, use_container_width=True)

else:
    st.warning("⚠️ Could not fetch coordinates for selected cities.")

st.markdown("---")

# ===============================
# 20 PROFESSIONAL GRAPHS
# ===============================
st.subheader("📊 Flight Analytics Charts (20 Graphs)")

charts = []
charts.append(px.histogram(filtered, x="Price", title="1. Price Distribution"))
charts.append(px.box(filtered, x="airline", y="Price", title="2. Airline Price Comparison"))
charts.append(px.pie(filtered, names="Total_stops", title="3. Stops Distribution"))
charts.append(px.bar(filtered["airline"].value_counts(), title="4. Flights per Airline"))
charts.append(px.bar(filtered["Source"].value_counts(), title="5. Flights per Source"))
charts.append(px.bar(filtered["destination"].value_counts(), title="6. Flights per Destination"))
charts.append(px.bar(filtered["route"].value_counts().head(10), title="7. Top 10 Routes"))
charts.append(px.line(filtered.sort_values("date_of_journey"),
                      x="date_of_journey", y="Price",
                      title="8. Price Trend Over Time"))
charts.append(px.scatter(filtered, x="Duration", y="Price", title="9. Duration vs Price"))
charts.append(px.bar(filtered.groupby("airline")["Price"].mean(), title="10. Avg Price per Airline"))
charts.append(px.bar(filtered.groupby("airline")["Price"].max(), title="11. Max Price per Airline"))
charts.append(px.bar(filtered.groupby("airline")["Price"].min(), title="12. Min Price per Airline"))
charts.append(px.bar(filtered.groupby("Source")["Price"].mean(), title="13. Avg Price by Source City"))
charts.append(px.bar(filtered.groupby("destination")["Price"].mean(), title="14. Avg Price by Destination City"))
charts.append(px.box(filtered, x="Total_stops", y="Price", title="15. Stops Impact on Price"))
charts.append(px.pie(filtered, names="airline", title="16. Airline Market Share"))
charts.append(px.density_heatmap(filtered, x="Source", y="destination", title="17. Source vs Destination Heatmap"))
charts.append(px.violin(filtered, x="airline", y="Price", title="18. Price Variability by Airline"))
charts.append(px.histogram(filtered, x="Duration", title="19. Duration Distribution"))
charts.append(px.histogram(filtered, x="Total_stops", color="airline", title="20. Stops Distribution by Airline"))

chart_names = [c.layout.title.text for c in charts]
selected_chart = st.selectbox("📌 Select Chart to Display", chart_names)

for chart in charts:
    if chart.layout.title.text == selected_chart:
        st.plotly_chart(chart, use_container_width=True)

st.subheader("📄 Flight Dataset Preview")
st.dataframe(filtered.head(30), use_container_width=True)

st.success("✅ Final Portfolio Dashboard Ready for Resume + Streamlit Cloud 🚀")
