import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
# EMPTY STATE (NO CRASH)
# ===============================
if len(airlines) == 0:
    st.title("✈️ Flight Analytics Dashboard")
    st.markdown("### Please select an Airline from sidebar to explore insights 🚀")

    st.info("Dataset contains thousands of flights across India with pricing & route details.")

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
    filtered = filtered[filtered["destinati]()]()
