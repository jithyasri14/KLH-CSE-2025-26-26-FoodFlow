from pathlib import Path
import sqlite3
import time
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

ROOT = Path(__file__).resolve().parents[2]
DATABASE = ROOT / "data" / "processed" / "foodflow_realtime.db"
INTEGRATED_FILE = ROOT / "data" / "processed" / "foodflow_integrated.csv"

def ensure_control_table():
    with sqlite3.connect(DATABASE) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS dashboard_control (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                paused INTEGER NOT NULL DEFAULT 0
            )
        """)
        connection.execute(
            "INSERT OR IGNORE INTO dashboard_control (id, paused) VALUES (1, 0)"
        )

def get_pipeline_paused():
    ensure_control_table()
    with sqlite3.connect(DATABASE) as connection:
        row = connection.execute(
            "SELECT paused FROM dashboard_control WHERE id = 1"
        ).fetchone()
    return bool(row[0])

def set_pipeline_paused(paused):
    ensure_control_table()
    with sqlite3.connect(DATABASE) as connection:
        connection.execute(
            "UPDATE dashboard_control SET paused = ? WHERE id = 1",
            (int(paused),),
        )

def reset_analysis():
    ensure_control_table()
    with sqlite3.connect(DATABASE) as connection:
        connection.execute("DELETE FROM realtime_orders")
        connection.execute(
            "DELETE FROM sqlite_sequence WHERE name = 'realtime_orders'"
        )
        connection.execute("UPDATE dashboard_control SET paused = 0 WHERE id = 1")

st.set_page_config(
    page_title="FoodFlow: End-to-End Food Delivery Data Engineering and Analytics Platform",
    layout="wide",
    initial_sidebar_state="expanded",
)

refresh_seconds = st.sidebar.select_slider(
    "Refresh interval",
    options=[3, 5, 10, 15, 30, 60],
    value=3,
    format_func=lambda seconds: f"Every {seconds} seconds",
)
st_autorefresh(interval=refresh_seconds * 1000, key="foodflow_live_refresh")

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .main {background: #0b1020;}
    [data-testid="stAppViewContainer"] {background: #0b1020;}
    [data-testid="stSidebar"] {background: #11182c;}
    [data-testid="stAppViewContainer"] {overflow: hidden;}
    .block-container {
        position: relative;
        z-index: 1;
        transform: translateZ(0);
    }
    .particle-field {
        position: fixed;
        inset: 0;
        z-index: 0;
        pointer-events: none;
        overflow: hidden;
        opacity: .7;
    }
    .particle {
        position: absolute;
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background: #53d8c2;
        box-shadow: 0 0 14px #53d8c2;
        animation: particle-drift 14s linear infinite;
    }
    .particle:nth-child(1) {left: 8%; top: 76%; animation-delay: -2s; animation-duration: 17s;}
    .particle:nth-child(2) {left: 19%; top: 24%; animation-delay: -7s; animation-duration: 13s; background: #62a8e8; box-shadow: 0 0 14px #62a8e8;}
    .particle:nth-child(3) {left: 34%; top: 88%; animation-delay: -11s; animation-duration: 19s;}
    .particle:nth-child(4) {left: 48%; top: 15%; animation-delay: -4s; animation-duration: 15s; background: #ef6f8f; box-shadow: 0 0 14px #ef6f8f;}
    .particle:nth-child(5) {left: 64%; top: 68%; animation-delay: -9s; animation-duration: 18s;}
    .particle:nth-child(6) {left: 79%; top: 32%; animation-delay: -1s; animation-duration: 14s; background: #62a8e8; box-shadow: 0 0 14px #62a8e8;}
    .particle:nth-child(7) {left: 91%; top: 82%; animation-delay: -6s; animation-duration: 16s;}
    .data-object {
        position: absolute;
        width: 16px;
        height: 16px;
        border: 1px solid rgba(123, 200, 181, .42);
        transform: rotate(45deg);
        animation: object-float 11s ease-in-out infinite;
    }
    .data-object:nth-child(8) {left: 14%; top: 48%; animation-delay: -3s;}
    .data-object:nth-child(9) {left: 73%; top: 19%; width: 10px; height: 10px; border-color: rgba(143, 170, 220, .5); animation-delay: -8s;}
    .data-object:nth-child(10) {left: 86%; top: 63%; width: 22px; height: 22px; border-color: rgba(212, 154, 184, .38); animation-delay: -6s;}
    .data-stream {
        position: absolute;
        width: 150px;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(123, 200, 181, .28), transparent);
        transform: rotate(-24deg);
        animation: stream-drift 13s ease-in-out infinite;
    }
    .data-stream:nth-child(11) {left: 3%; top: 36%; animation-delay: -5s;}
    .data-stream:nth-child(12) {right: 4%; top: 47%; transform: rotate(28deg); background: linear-gradient(90deg, transparent, rgba(143, 170, 220, .25), transparent); animation-delay: -9s;}
    @keyframes particle-drift {
        0% {transform: translate3d(0, 25vh, 0) scale(.65); opacity: 0;}
        15%, 75% {opacity: .7;}
        100% {transform: translate3d(5vw, -35vh, 0) scale(1.15); opacity: 0;}
    }
    @keyframes object-float {
        0%, 100% {opacity: .18; transform: translate3d(0, 0, 0) rotate(45deg) scale(.85);}
        50% {opacity: .55; transform: translate3d(18px, -24px, 0) rotate(135deg) scale(1.1);}
    }
    @keyframes stream-drift {
        0%, 100% {opacity: .18; transform: translateX(-12px) rotate(-24deg);}
        50% {opacity: .55; transform: translateX(28px) rotate(-24deg);}
    }
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #18243d, #111a30);
        border: 1px solid #2b3b5d;
        padding: 14px;
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(0,0,0,.18);
        transition: transform .28s ease, box-shadow .28s ease, border-color .28s ease;
        will-change: transform;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px) scale(1.015);
        border-color: #7bc8b5;
        box-shadow: 0 12px 28px rgba(0, 0, 0, .3), 0 0 18px rgba(123, 200, 181, .12);
    }
    .hero {
        padding: 22px 26px;
        border-radius: 20px;
        background: linear-gradient(115deg, #172b4d, #243b70 55%, #3a235f);
        border: 1px solid #3e5687;
        margin-bottom: 18px;
        animation: hero-enter .7s ease-out both;
    }
    .hero h1 {margin: 0; font-size: 2.35rem;}
    .hero p {margin: 8px 0 0; color: #d7e3ff; letter-spacing: .02em;}
    .status-pill {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 999px;
        background: #123d31;
        color: #8ff0c5;
        font-size: .85rem;
        font-weight: 700;
        animation: live-pulse 2s ease-in-out infinite;
    }
    .section-title {font-size: 1.25rem; font-weight: 700; margin-top: 10px;}
    div[data-testid="stDataFrame"] {border-radius: 14px; overflow: hidden;}
    .stream-card {
        padding: 15px 18px;
        border: 1px solid #2b4c6c;
        border-left: 4px solid #53d8c2;
        border-radius: 14px;
        background: linear-gradient(105deg, #112238, #142c43);
        margin-bottom: 16px;
        animation: signal-enter .6s ease-out both;
        transition: transform .3s ease, box-shadow .3s ease, border-color .3s ease;
        will-change: transform;
    }
    .stream-card:hover {
        transform: translate3d(4px, -5px, 0) scale(1.015);
        border-color: #7bc8b5;
        box-shadow: 0 12px 26px rgba(0, 0, 0, .28), 0 0 18px rgba(123, 200, 181, .12);
    }
    .stream-label {color: #9ab8ce; font-size: .78rem; text-transform: uppercase; letter-spacing: .1em;}
    .stream-value {color: #e7fbf7; font-size: 1.4rem; font-weight: 700;}
    @keyframes hero-enter {from {opacity: 0; transform: translateY(-10px);} to {opacity: 1; transform: translateY(0);}}
    @keyframes signal-enter {from {opacity: 0; transform: translateY(8px);} to {opacity: 1; transform: translateY(0);}}
    @keyframes live-pulse {0%, 100% {box-shadow: 0 0 0 0 rgba(83, 216, 194, .15);} 50% {box-shadow: 0 0 0 7px rgba(83, 216, 194, 0);}}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="particle-field" aria-hidden="true">
        <span class="particle"></span><span class="particle"></span>
        <span class="particle"></span><span class="particle"></span>
        <span class="particle"></span><span class="particle"></span>
        <span class="particle"></span>
        <span class="data-object"></span><span class="data-object"></span>
        <span class="data-object"></span><span class="data-stream"></span>
        <span class="data-stream"></span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Header ----------
st.markdown(
    f"""
    <div class="hero">
        <h1>FoodFlow: End-to-End Food Delivery Data Engineering and Analytics Platform</h1>
        <p>Unified food-delivery data • Realtime ingestion • Decision-ready analytics</p>
        <br><span class="status-pill">● LIVE SYSTEM · Last sync {time.strftime('%H:%M:%S')}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

if not DATABASE.exists():
    st.warning("The real-time database does not exist yet.")
    st.info("Start the pipeline using: `python src/streaming/realtime_pipeline.py`")
    st.stop()

st.sidebar.title("Control Panel")
st.sidebar.caption(
    f"Manage the realtime ingestion stream · refreshes every {refresh_seconds} seconds"
)
paused = get_pipeline_paused()
pause_label = "Resume pipeline" if paused else "Pause pipeline"
if st.sidebar.button(pause_label, use_container_width=True):
    set_pipeline_paused(not paused)
    st.rerun()

if st.sidebar.button("Reset analysis", use_container_width=True):
    reset_analysis()
    st.rerun()

if paused:
    st.sidebar.warning("Pipeline paused. Existing analysis is preserved.")
else:
    st.sidebar.success("Pipeline running. New orders are being analyzed.")

try:
    with sqlite3.connect(DATABASE) as connection:
        df = pd.read_sql_query("SELECT * FROM realtime_orders ORDER BY id DESC", connection)
except Exception as exc:
    st.error(f"Could not read the real-time database: {exc}")
    st.stop()

if df.empty:
    st.info("Waiting for incoming orders from the real-time pipeline...")
    st.stop()

# ---------- Sidebar filters ----------
predictions = sorted(df["prediction"].dropna().unique().tolist())
selected_predictions = st.sidebar.multiselect(
    "Prediction categories",
    predictions,
    default=predictions,
)

min_value = float(df["order_value"].min())
max_value = float(df["order_value"].max())
if min_value == max_value:
    value_range = (min_value, max_value)
else:
    value_range = st.sidebar.slider(
        "Order value range",
        min_value=min_value,
        max_value=max_value,
        value=(min_value, max_value),
    )

search_text = st.sidebar.text_input("Search prediction", placeholder="Cancelled, Delayed...")
show_rows = st.sidebar.slider("Rows to display", 5, 50, 15)

filtered = df[
    df["prediction"].isin(selected_predictions)
    & df["order_value"].between(value_range[0], value_range[1])
].copy()

if search_text:
    filtered = filtered[
        filtered["prediction"].astype(str).str.contains(search_text, case=False, na=False)
    ]

# ---------- KPI cards ----------
total = len(filtered)
cancelled = int((filtered["prediction"] == "Cancelled").sum())
delayed = int((filtered["prediction"] == "Delayed").sum())
on_time = int((filtered["prediction"] == "On-Time").sum())

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Live Events", total)
c2.metric("Cancelled", cancelled)
c3.metric("Delayed", delayed)
c4.metric("On-Time", on_time)
c5.metric("Live Value", f"₹{filtered['order_value'].sum():,.0f}")

if filtered.empty:
    st.warning("No orders match the selected filters.")
    st.stop()

# ---------- Tabs ----------
tab_overview, tab_live, tab_insights = st.tabs([
    "Platform Overview", "Realtime Stream", "Operational ML"
])

with tab_overview:
    if INTEGRATED_FILE.exists():
        integrated = pd.read_csv(INTEGRATED_FILE)
        integrated["order_date"] = pd.to_datetime(integrated["order_date"])
        source_count = 6

        st.markdown('<div class="section-title">Integrated Data Landscape</div>', unsafe_allow_html=True)
        snapshot = st.columns(5)
        snapshot[0].metric("Source Domains", source_count, "Customers, restaurants, orders, payments, deliveries, reviews")
        snapshot[1].metric("Integrated Rows", f"{len(integrated):,}")
        snapshot[2].metric("Customers", f"{integrated['customer_id'].nunique():,}")
        snapshot[3].metric("Restaurants", f"{integrated['restaurant_id'].nunique():,}")
        snapshot[4].metric("Revenue", f"₹{integrated['order_value'].sum():,.0f}")

        city_df = integrated.groupby("customer_city", as_index=False)["order_value"].sum().sort_values("order_value", ascending=False)
        cuisine_df = integrated.groupby("cuisine", as_index=False).agg(
            Orders=("order_id", "count"), Average_Rating=("restaurant_rating", "mean")
        ).sort_values("Orders", ascending=False)
        domain_left, domain_right = st.columns(2)
        with domain_left:
            city_fig = px.bar(
                city_df,
                x="customer_city",
                y="order_value",
                color="customer_city",
                title="Revenue by customer city",
                template="plotly_dark",
                color_discrete_sequence=["#7bc8b5", "#8faadc", "#d49ab8", "#a9b7e3", "#a8c6a0"],
            )
            city_fig.update_layout(height=330, showlegend=False, margin=dict(l=10, r=10, t=55, b=10))
            st.plotly_chart(city_fig, use_container_width=True)
        with domain_right:
            cuisine_fig = px.bar(
                cuisine_df,
                x="cuisine",
                y="Orders",
                color="cuisine",
                title="Order volume by cuisine",
                template="plotly_dark",
                color_discrete_sequence=["#8faadc", "#7bc8b5", "#d49ab8", "#a9b7e3", "#a8c6a0"],
            )
            cuisine_fig.update_layout(height=330, showlegend=False, margin=dict(l=10, r=10, t=55, b=10))
            st.plotly_chart(cuisine_fig, use_container_width=True)

        st.markdown('<div class="section-title">Operational Signals</div>', unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        st.markdown('<div class="section-title">Prediction Distribution</div>', unsafe_allow_html=True)
        counts = filtered["prediction"].value_counts().reset_index()
        counts.columns = ["Prediction", "Count"]
        fig = px.bar(
            counts,
            x="Prediction",
            y="Count",
            color="Prediction",
            text="Count",
            template="plotly_dark",
            title="Live order outcome categories",
            color_discrete_map={
                "Cancelled": "#d49ab8",
                "Delayed": "#8faadc",
                "On-Time": "#7bc8b5",
            },
        )
        fig.update_layout(height=360, showlegend=False, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown('<div class="section-title">Average Model Confidence</div>', unsafe_allow_html=True)
        probability_df = pd.DataFrame({
            "Category": ["Cancelled", "Delayed", "On-Time"],
            "Probability": [
                filtered["cancelled_probability"].mean() * 100,
                filtered["delayed_probability"].mean() * 100,
                filtered["on_time_probability"].mean() * 100,
            ],
        })
        fig = px.bar(
            probability_df,
            x="Category",
            y="Probability",
            color="Category",
            text=probability_df["Probability"].round(1).astype(str) + "%",
            template="plotly_dark",
            title="Average probability by prediction class",
            color_discrete_map={
                "Cancelled": "#d49ab8",
                "Delayed": "#8faadc",
                "On-Time": "#7bc8b5",
            },
        )
        fig.update_yaxes(range=[0, 100], title="Probability (%)")
        fig.update_layout(height=360, showlegend=False, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Order Value Trend</div>', unsafe_allow_html=True)
    time_df = filtered.sort_values("order_timestamp").copy()
    fig = px.line(
        time_df,
        x="order_timestamp",
        y="order_value",
        color="prediction",
        markers=True,
        template="plotly_dark",
        title="Incoming order value over time",
        color_discrete_map={
            "Cancelled": "#d49ab8",
            "Delayed": "#8faadc",
            "On-Time": "#7bc8b5",
        },
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=55, b=10),
        hovermode="x unified",
        legend_title_text="Outcome",
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_live:
    st.subheader("Realtime Ingestion Stream")
    latest = filtered.iloc[0]
    stream_col1, stream_col2, stream_col3 = st.columns(3)
    with stream_col1:
        st.markdown(
            f'<div class="stream-card"><div class="stream-label">Latest signal</div>'
            f'<div class="stream-value">{latest["prediction"]}</div></div>',
            unsafe_allow_html=True,
        )
    with stream_col2:
        st.markdown(
            f'<div class="stream-card"><div class="stream-label">Order value</div>'
            f'<div class="stream-value">₹{float(latest["order_value"]):,.2f}</div></div>',
            unsafe_allow_html=True,
        )
    with stream_col3:
        st.markdown(
            f'<div class="stream-card"><div class="stream-label">Stream position</div>'
            f'<div class="stream-value">#{int(latest["id"]):,}</div></div>',
            unsafe_allow_html=True,
        )

    pulse_df = filtered.head(20).sort_values("id").copy()
    pulse_fig = px.line(
        pulse_df,
        x="id",
        y="order_value",
        markers=True,
        template="plotly_dark",
        title="Live stream pulse",
    )
    pulse_fig.update_traces(line=dict(color="#53d8c2", width=3), marker=dict(size=8))
    pulse_fig.update_layout(
        height=270,
        margin=dict(l=10, r=10, t=55, b=10),
        xaxis_title="Recent event",
        yaxis_title="Order value",
    )
    st.plotly_chart(pulse_fig, use_container_width=True)

    display_columns = [
        "id", "order_timestamp", "order_value", "delivery_distance_km",
        "preparation_time_min", "estimated_delivery_time_min",
        "restaurant_rating", "customer_age", "prediction",
    ]
    available_columns = [c for c in display_columns if c in filtered.columns]
    st.dataframe(filtered[available_columns].head(show_rows), use_container_width=True, hide_index=True)

    csv_data = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered live data",
        data=csv_data,
        file_name="foodflow_live_orders.csv",
        mime="text/csv",
    )

    st.markdown("### Latest Prediction")
    p1, p2, p3 = st.columns(3)
    p1.metric("Prediction", str(latest["prediction"]))
    p2.metric("Order Value", f"₹{float(latest['order_value']):,.2f}")
    p3.metric("Restaurant Rating", f"{float(latest['restaurant_rating']):.1f} ⭐")

with tab_insights:
    st.subheader("Model Confidence Monitor")
    probability_cols = [
        "cancelled_probability", "delayed_probability", "on_time_probability"
    ]
    available_probability_cols = [c for c in probability_cols if c in filtered.columns]
    confidence = filtered[available_probability_cols].mean().sort_values(ascending=False) * 100

    gauge_col, table_col = st.columns([1, 1])
    with gauge_col:
        top_class = confidence.index[0].replace("_probability", "").replace("_", " ").title()
        top_value = float(confidence.iloc[0])
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=top_value,
            title={"text": f"Most likely class: {top_class}"},
            gauge={"axis": {"range": [0, 100]}, "bar": {"thickness": 0.35}},
        ))
        gauge.update_layout(template="plotly_dark", height=300, margin=dict(l=20, r=20, t=70, b=10))
        st.plotly_chart(gauge, use_container_width=True)

    with table_col:
        st.markdown("#### Average probabilities")
        st.dataframe(
            pd.DataFrame({"Class": confidence.index, "Average probability (%)": confidence.round(2).values}),
            use_container_width=True,
            hide_index=True,
        )

st.caption(f"Last dashboard refresh: {time.strftime('%H:%M:%S')} • Showing {len(filtered)} of {len(df)} records")
