import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="Flight Analytics Pro Dashboard",
    page_icon="✈️",
    layout="wide"
)

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data():
    df = pd.read_csv("flights.csv")
    df["date_of_journey"] = pd.to_datetime(df["date_of_journey"])
    return df

df = load_data()

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.title("🔍 Flight Filters")

airline_filter = st.sidebar.multiselect(
    "Select Airline",
    df["airline"].unique(),
    default=df["airline"].unique()[:5]
)

source_filter = st.sidebar.multiselect(
    "Select Source City",
    df["Source"].unique(),
    default=df["Source"].unique()[:5]
)

dest_filter = st.sidebar.multiselect(
    "Select Destination City",
    df["destination"].unique(),
    default=df["destination"].unique()[:5]
)

filtered_df = df[
    (df["airline"].isin(airline_filter)) &
    (df["Source"].isin(source_filter)) &
    (df["destination"].isin(dest_filter))
]

# ==============================
# HEADER
# ==============================
st.title("✈️ Flight Analytics Pro Dashboard")
st.markdown(
    "### A complete interactive dashboard for airline pricing, routes, trends & insights"
)

# ==============================
# AIRLINE LOGOS
# ==============================
st.subheader("🏢 Selected Airlines")

logo_folder = "airline_logos"
cols = st.columns(6)

for i, airline in enumerate(airline_filter[:6]):
    logo_path = os.path.join(logo_folder, f"{airline}.png")

    with cols[i]:
        if os.path.exists(logo_path):
            st.image(logo_path, width=80)
        else:
            st.info(airline)

# ==============================
# KPI METRICS
# ==============================
st.subheader("📌 Quick Flight Insights")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Flights", filtered_df.shape[0])
c2.metric("Average Price", f"₹ {filtered_df['Price'].mean():.0f}")
c3.metric("Highest Price", f"₹ {filtered_df['Price'].max():.0f}")
c4.metric("Lowest Price", f"₹ {filtered_df['Price'].min():.0f}")

st.markdown("---")

# ==============================
# DASHBOARD TABS (Categories)
# ==============================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📍 Overview", "💰 Price Analytics", "🛫 Airline Insights",
     "🗺️ Routes & Stops", "📥 Trends & Download"]
)

# ==========================================================
# TAB 1: OVERVIEW
# ==========================================================
with tab1:
    st.subheader("📍 Flights Overview")

    fig1 = px.bar(
        filtered_df["airline"].value_counts(),
        title="Flights Count by Airline"
    )
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.pie(
        filtered_df,
        names="Total_stops",
        title="Stops Distribution"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(filtered_df.head(15), use_container_width=True)


# ==========================================================
# TAB 2: PRICE ANALYTICS
# ==========================================================
with tab2:
    st.subheader("💰 Flight Price Analytics")

    fig3 = px.histogram(
        filtered_df,
        x="Price",
        nbins=40,
        title="Price Distribution of Flights"
    )
    st.plotly_chart(fig3, use_container_width=True)

    fig4 = px.box(
        filtered_df,
        x="airline",
        y="Price",
        title="Airline-wise Price Comparison"
    )
    st.plotly_chart(fig4, use_container_width=True)

    fig5 = px.scatter(
        filtered_df,
        x="Duration",
        y="Price",
        color="airline",
        title="Duration vs Price Relationship"
    )
    st.plotly_chart(fig5, use_container_width=True)


# ==========================================================
# TAB 3: AIRLINE INSIGHTS
# ==========================================================
with tab3:
    st.subheader("🛫 Airline Performance Insights")

    fig6 = px.bar(
        filtered_df.groupby("airline")["Price"].mean().sort_values(),
        title="Average Ticket Price by Airline"
    )
    st.plotly_chart(fig6, use_container_width=True)

    fig7 = px.bar(
        filtered_df.groupby("airline")["Price"].max().sort_values(),
        title="Highest Ticket Price by Airline"
    )
    st.plotly_chart(fig7, use_container_width=True)

    fig8 = px.bar(
        filtered_df.groupby("airline")["Price"].min().sort_values(),
        title="Lowest Ticket Price by Airline"
    )
    st.plotly_chart(fig8, use_container_width=True)


# ==========================================================
# TAB 4: ROUTES & STOPS
# ==========================================================
with tab4:
    st.subheader("🗺️ Routes & Stops Analytics")

    fig9 = px.bar(
        filtered_df["route"].value_counts().head(10),
        title="Top 10 Most Frequent Routes"
    )
    st.plotly_chart(fig9, use_container_width=True)

    fig10 = px.box(
        filtered_df,
        x="Total_stops",
        y="Price",
        title="Stops Impact on Ticket Price"
    )
    st.plotly_chart(fig10, use_container_width=True)

    fig11 = px.bar(
        filtered_df.groupby("Source")["Price"].mean(),
        title="Average Price by Source City"
    )
    st.plotly_chart(fig11, use_container_width=True)


# ==========================================================
# TAB 5: TRENDS + DOWNLOAD
# ==========================================================
with tab5:
    st.subheader("📈 Flight Trends & Download Center")

    fig12 = px.line(
        filtered_df.sort_values("date_of_journey"),
        x="date_of_journey",
        y="Price",
        title="Price Trend Over Time"
    )
    st.plotly_chart(fig12, use_container_width=True)

    st.download_button(
        "⬇️ Download Filtered Flight Dataset",
        filtered_df.to_csv(index=False),
        file_name="filtered_flights.csv",
        mime="text/csv"
    )

    st.success("✅ Download Ready & Report Section Included")

# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.info("✨ Built with Streamlit + Plotly | Flight Analytics Dashboard Pro Project")
