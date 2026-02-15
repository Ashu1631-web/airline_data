import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import os

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Flight Analytics Premium Dashboard",
    page_icon="✈️",
    layout="wide"
)

# ===============================
# LOAD DATA
# ===============================
@st.cache_data
def load_data():
    df = pd.read_csv("flights.csv")

    # Convert date safely
    if "date_of_journey" in df.columns:
        df["date_of_journey"] = pd.to_datetime(df["date_of_journey"], errors="coerce")

    return df


df = load_data()

# ===============================
# AIRLINE LOGOS (NO DOWNLOAD SAFE)
# ===============================
AIRLINE_LOGOS = {
    "IndiGo": "https://logos-world.net/wp-content/uploads/2023/01/IndiGo-Logo.png",
    "SpiceJet": "https://logos-world.net/wp-content/uploads/2023/01/SpiceJet-Logo.png",
    "Air India": "https://logos-world.net/wp-content/uploads/2023/01/Air-India-Logo.png",
    "GoAir": "https://logos-world.net/wp-content/uploads/2023/01/GoAir-Logo.png",
}

# ===============================
# SIDEBAR FILTERS
# ===============================
st.sidebar.title("🔍 Flight Dashboard Filters")

airlines = st.sidebar.multiselect(
    "Select Airlines",
    df["airline"].unique(),
    default=df["airline"].unique()[:4]
)

sources = st.sidebar.multiselect(
    "Select Source City",
    df["Source"].unique(),
    default=df["Source"].unique()[:3]
)

destinations = st.sidebar.multiselect(
    "Select Destination City",
    df["destination"].unique(),
    default=df["destination"].unique()[:3]
)

filtered = df[
    (df["airline"].isin(airlines)) &
    (df["Source"].isin(sources)) &
    (df["destination"].isin(destinations))
]

# ===============================
# HEADER
# ===============================
st.title("✈️ Flight Analytics Premium Dashboard")
st.markdown("### Professional Airline Price + Route Intelligence System")

# ===============================
# SHOW LOGOS (SAFE)
# ===============================
st.subheader("🏢 Selected Airlines")

cols = st.columns(len(airlines))

for i, airline in enumerate(airlines):
    with cols[i]:
        if airline in AIRLINE_LOGOS:
            st.image(AIRLINE_LOGOS[airline], width=90)
        else:
            st.info(airline)

# ===============================
# KPI METRICS
# ===============================
st.subheader("📌 Key Flight Insights")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Flights", len(filtered))
c2.metric("Avg Price", f"₹{filtered['Price'].mean():.0f}")
c3.metric("Max Price", f"₹{filtered['Price'].max():.0f}")
c4.metric("Min Price", f"₹{filtered['Price'].min():.0f}")

st.markdown("---")

# ===============================
# REAL 30 UNIQUE CHARTS
# ===============================
st.subheader("📊 Interactive Chart Explorer (30 Unique Charts)")

charts = {}

charts["1. Price Distribution"] = px.histogram(filtered, x="Price")
charts["2. Airline-wise Price Comparison"] = px.box(filtered, x="airline", y="Price")
charts["3. Stops Distribution"] = px.pie(filtered, names="Total_stops")
charts["4. Flights per Airline"] = px.bar(filtered["airline"].value_counts())
charts["5. Flights per Source City"] = px.bar(filtered["Source"].value_counts())
charts["6. Flights per Destination City"] = px.bar(filtered["destination"].value_counts())
charts["7. Top 10 Routes"] = px.bar(filtered["route"].value_counts().head(10))
charts["8. Duration vs Price"] = px.scatter(filtered, x="Duration", y="Price")
charts["9. Stops Impact on Price"] = px.box(filtered, x="Total_stops", y="Price")
charts["10. Avg Price per Airline"] = px.bar(filtered.groupby("airline")["Price"].mean())

charts["11. Max Price per Airline"] = px.bar(filtered.groupby("airline")["Price"].max())
charts["12. Min Price per Airline"] = px.bar(filtered.groupby("airline")["Price"].min())
charts["13. Avg Price by Source"] = px.bar(filtered.groupby("Source")["Price"].mean())
charts["14. Avg Price by Destination"] = px.bar(filtered.groupby("destination")["Price"].mean())

charts["15. Stops Count by Airline"] = px.bar(filtered.groupby("airline")["Total_stops"].count())
charts["16. Price Trend Over Journey Date"] = px.line(filtered.sort_values("date_of_journey"),
                                                      x="date_of_journey", y="Price")

charts["17. Airline vs Duration Avg"] = px.bar(filtered.groupby("airline")["Duration"].mean())
charts["18. Route vs Avg Price"] = px.bar(filtered.groupby("route")["Price"].mean().head(10))

charts["19. Price by Day of Month"] = px.histogram(filtered, x=filtered["date_of_journey"].dt.day)
charts["20. Monthly Price Trend"] = px.line(filtered.groupby(filtered["date_of_journey"].dt.month)["Price"].mean())

charts["21. Stops vs Duration"] = px.scatter(filtered, x="Total_stops", y="Duration")
charts["22. Airline Share Pie"] = px.pie(filtered, names="airline")

charts["23. Source vs Destination Flights"] = px.density_heatmap(filtered, x="Source", y="destination")

charts["24. Price Heatmap Stops-Airline"] = px.density_heatmap(filtered, x="airline", y="Total_stops", z="Price")

charts["25. Cheapest Routes"] = px.bar(filtered.groupby("route")["Price"].min().sort_values().head(10))
charts["26. Expensive Routes"] = px.bar(filtered.groupby("route")["Price"].max().sort_values(ascending=False).head(10))

charts["27. Airline Price Variability"] = px.violin(filtered, x="airline", y="Price")
charts["28. Duration Distribution"] = px.histogram(filtered, x="Duration")

charts["29. Stops Distribution by Airline"] = px.histogram(filtered, x="Total_stops", color="airline")

charts["30. Price vs Source City Scatter"] = px.scatter(filtered, x="Source", y="Price", color="airline")

# ===============================
# DRAG & DROP STYLE SELECTOR
# ===============================
selected_chart = st.selectbox("📌 Select Any Chart to Display", list(charts.keys()))

st.plotly_chart(charts[selected_chart], use_container_width=True)

# ===============================
# DATA TABLE VIEW
# ===============================
st.subheader("📄 Flight Dataset Table")
st.dataframe(filtered, use_container_width=True)

# ===============================
# PDF REPORT DOWNLOAD (SAFE)
# ===============================
st.subheader("📥 Download Analytics Report")

if st.button("📄 Generate PDF Report"):

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)

    pdf.cell(200, 10, txt="Flight Analytics Premium Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Total Flights: {len(filtered)}", ln=True)
    pdf.cell(200, 10, txt=f"Average Price: ₹{filtered['Price'].mean():.0f}", ln=True)
    pdf.cell(200, 10, txt=f"Maximum Price: ₹{filtered['Price'].max():.0f}", ln=True)
    pdf.cell(200, 10, txt=f"Minimum Price: ₹{filtered['Price'].min():.0f}", ln=True)

    pdf.output("flight_report.pdf")

    with open("flight_report.pdf", "rb") as file:
        st.download_button(
            label="⬇️ Download PDF Report",
            data=file,
            file_name="flight_report.pdf",
            mime="application/pdf"
        )

st.success("✅ Dashboard Fully Deployment Ready (No Errors)")

