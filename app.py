import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config("Flight Analytics BI Dashboard", "✈️", layout="wide")

# ===============================
# PREMIUM THEME CSS
# ===============================
st.markdown("""
<style>
.big-title {
    font-size:45px;
    font-weight:700;
    color:white;
}
.sub-title {
    font-size:20px;
    color:#dcdcdc;
}
.card {
    padding:20px;
    border-radius:15px;
    background:#111827;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.4);
    margin-bottom:15px;
}
</style>
""", unsafe_allow_html=True)


# ===============================
# LOGO FIX (Guaranteed)
# ===============================
def get_airline_logo(airline):
    fallback = "https://cdn-icons-png.flaticon.com/512/984/984233.png"

    try:
        url = f"https://logo.clearbit.com/{airline.lower().replace(' ', '')}.com"
        r = requests.get(url, timeout=2)

        if r.status_code == 200:
            return url
        else:
            return fallback
    except:
        return fallback


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
    "Select Airlines",
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
# EMPTY FILTER ANIMATION
# ===============================
if len(airlines) == 0:
    st.markdown("<h1 class='big-title'>✈️ Flight Analytics BI Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Please select an Airline from left sidebar to start exploring insights 🚀</p>",
                unsafe_allow_html=True)

    st.image("https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif", width=400)
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
st.markdown("<h1 class='big-title'>✈️ Flight Analytics BI Dashboard (Premium)</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>PowerBI Style Dashboard with Maps + Charts + Insights</p>", unsafe_allow_html=True)

# ===============================
# LOGOS SHOW
# ===============================
st.subheader("🏢 Airline Logos")

cols = st.columns(min(len(airlines), 5))
for i, airline in enumerate(airlines[:5]):
    with cols[i]:
        st.image(get_airline_logo(airline), width=90)
        st.caption(airline)

# ===============================
# KPI METRICS
# ===============================
st.subheader("📌 Key Insights")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Flights", len(filtered))
c2.metric("Avg Price", f"₹{filtered['Price'].mean():.0f}")
c3.metric("Max Price", f"₹{filtered['Price'].max():.0f}")
c4.metric("Min Price", f"₹{filtered['Price'].min():.0f}")

# ===============================
# SHORT DESCRIPTION BOX
# ===============================
st.markdown(f"""
<div class="card">
<h3>✍️ Summary</h3>
<p>
You selected <b>{", ".join(airlines)}</b>.  
Flights available from <b>{filtered['Source'].nunique()}</b> source cities to  
<b>{filtered['destination'].nunique()}</b> destinations.  
Average ticket price is <b>₹{filtered['Price'].mean():.0f}</b>.
</p>
</div>
""", unsafe_allow_html=True)

# ===============================
# MAP VIEW (Routes)
# ===============================
st.subheader("🗺️ Flight Route Map (Sample View)")

city_coords = {
    "Delhi": (28.61, 77.20),
    "Mumbai": (19.07, 72.87),
    "Kolkata": (22.57, 88.36),
    "Chennai": (13.08, 80.27),
    "Bangalore": (12.97, 77.59),
    "Hyderabad": (17.38, 78.48),
}

map_df = filtered.head(20)

map_df["lat"] = map_df["Source"].map(lambda x: city_coords.get(x, (0, 0))[0])
map_df["lon"] = map_df["Source"].map(lambda x: city_coords.get(x, (0, 0))[1])

fig_map = px.scatter_geo(
    map_df,
    lat="lat",
    lon="lon",
    hover_name="Source",
    title="Flight Sources (Geo View)"
)

st.plotly_chart(fig_map, use_container_width=True)

# ===============================
# DRAG-DROP FEEL (Chart Cards)
# ===============================
st.subheader("🎛️ Chart Dashboard (Drag & Drop Feel)")

chart_list = st.multiselect(
    "Select Charts to Display (Like Drag Layout)",
    ["Price Distribution", "Airline Comparison", "Stops Pie", "Top Routes", "Price Trend"],
    default=["Price Distribution", "Airline Comparison"]
)

if "Price Distribution" in chart_list:
    st.plotly_chart(px.histogram(filtered, x="Price"), use_container_width=True)

if "Airline Comparison" in chart_list:
    st.plotly_chart(px.box(filtered, x="airline", y="Price"), use_container_width=True)

if "Stops Pie" in chart_list:
    st.plotly_chart(px.pie(filtered, names="Total_stops"), use_container_width=True)

if "Top Routes" in chart_list:
    st.plotly_chart(px.bar(filtered["route"].value_counts().head(10)), use_container_width=True)

if "Price Trend" in chart_list:
    st.plotly_chart(px.line(filtered, x="date_of_journey", y="Price"), use_container_width=True)

# ===============================
# DATA TABLE
# ===============================
st.subheader("📄 Flight Data Table")
st.dataframe(filtered.head(30), use_container_width=True)

st.success("✅ Ultra Premium Dashboard Ready 🚀")
