import streamlit as st
import snowflake.connector
import pandas as pd
import altair as alt

# 1. Page Configuration
st.set_page_config(page_title="Snowflake Telemetry Data Explorer", layout="wide")
st.title("📊 Snowflake Live Data Engine")

# 2. Connection Initialization
@st.cache_resource
def init_connection():
    return snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"]
    )

try:
    conn = init_connection()
except Exception as e:
    st.error(f"Failed to connect to Snowflake: {e}")
    st.stop()

# ⚡ OPTIMIZATION & BUG FIX: Properly unpack row[0] from the tuple list
@st.cache_data(ttl=3600)
def get_filter_options(column_name):
    query = f"SELECT DISTINCT {column_name} FROM trending_analytics_db.ai_telemetry.ai_agent_interactions WHERE {column_name} IS NOT NULL ORDER BY {column_name};"
    with conn.cursor() as cur:
        cur.execute(query)
        # Fixes the tuple matching bug by extracting the exact string value
        return [row[0] for row in cur.fetchall()]

# ⚡ OPTIMIZATION: Handle query generation and fetching efficiently
@st.cache_data(ttl=600)
def load_filtered_data(geo, device):
    base_query = "SELECT * FROM trending_analytics_db.ai_telemetry.ai_agent_interactions WHERE 1=1"
    params = []
    
    if geo != "All Regions":
        base_query += " AND GEO_LOCATION = %s"
        params.append(geo)
        
    if device != "All Devices":
        base_query += " AND DEVICE_TYPE = %s"
        params.append(device)
        
    # Keeps browser charts fast, but sets a high upper limit for the payload
    base_query += " ORDER BY EVENT_TIMESTAMP DESC LIMIT 10000;"
    
    with conn.cursor() as cur:
        cur.execute(base_query, params)
        # Safely extract column names from description
        columns = [col[0] for col in cur.description]
        df = pd.DataFrame(cur.fetchall(), columns=columns)
        if "EVENT_TIMESTAMP" in df.columns:
            df["EVENT_TIMESTAMP"] = pd.to_datetime(df["EVENT_TIMESTAMP"])
        return df

# 3. SIDEBAR FILTERS
st.sidebar.header("🔍 Interactive Controls")

# Fetch operational dropdown options directly from Snowflake metadata
geo_options = ["All Regions"] + get_filter_options("GEO_LOCATION")
device_options = ["All Devices"] + get_filter_options("DEVICE_TYPE")

# Reset Filter Mechanism using Streamlit Session State
if "geo_index" not in st.session_state:
    st.session_state.geo_index = 0
if "device_index" not in st.session_state:
    st.session_state.device_index = 0

if st.sidebar.button("🔄 Reset Filters"):
    st.session_state.geo_index = 0
    st.session_state.device_index = 0
    st.rerun()

selected_geo = st.sidebar.selectbox("Select Region", geo_options, index=st.session_state.geo_index)
selected_device = st.sidebar.selectbox("Select Device Type", device_options, index=st.session_state.device_index)

# 4. Fetch the optimized dataset from Snowflake
with st.spinner("Streaming filtered data from Snowflake..."):
    df_filtered = load_filtered_data(selected_geo, selected_device)

# 5. VISUAL METRICS ROW
col1, col2, col3 = st.columns(3)
col1.metric("Available Records (View)", f"{len(df_filtered):,}")

if "SESSION_DURATION_SEC" in df_filtered.columns and not df_filtered.empty:
    col2.metric("Avg Session Duration", f"{int(df_filtered['SESSION_DURATION_SEC'].mean())}s")
else:
    col2.metric("Avg Session Duration", "0s")
    
if "AI_AGENT_ASSISTED" in df_filtered.columns and not df_filtered.empty:
    ai_pct = (df_filtered['AI_AGENT_ASSISTED'].astype(str).str.upper() == 'TRUE').mean() * 100
    col3.metric("AI Assisted Rate", f"{ai_pct:.1f}%")
else:
    col3.metric("AI Assisted Rate", "0.0%")

st.markdown("---")

# 6. TRENDING VISUAL MAPS
st.subheader("📈 Trending Visual Intelligence Maps")

if not df_filtered.empty:
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.write("**Top Interacting AI Personas**")
        if "USER_PERSONA" in df_filtered.columns:
            st.altair_chart(
                alt.Chart(df_filtered).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                    x=alt.X('USER_PERSONA:N', title='User Persona', sort='-y'),
                    y=alt.Y('count():Q', title='Total Interactions'),
                    color=alt.Color('USER_PERSONA:N', legend=None),
                    tooltip=['USER_PERSONA', 'count()']
                ).interactive(), 
                use_container_width=True
            )

    with chart_col2:
        st.write("**Session Duration Insights by Device**")
        if "EVENT_TIMESTAMP" in df_filtered.columns and "SESSION_DURATION_SEC" in df_filtered.columns:
            st.altair_chart(
                alt.Chart(df_filtered).mark_circle(size=60).encode(
                    x=alt.X('EVENT_TIMESTAMP:T', title='Event Timestamp'),
                    y=alt.Y('SESSION_DURATION_SEC:Q', title='Session Duration (Seconds)'),
                    color=alt.Color('DEVICE_TYPE:N', title='Device Type'),
                    tooltip=['USER_PERSONA', 'DEVICE_TYPE', 'SESSION_DURATION_SEC']
                ).interactive(),
                use_container_width=True
            )
else:
    st.info("No data elements currently match your active dropdown sidebar filters.")

st.markdown("---")

# 7. TELEMETRY DATA TABLE
st.subheader("📋 Raw Telemetry Data Stream")

search_query = st.text_input("🔍 Keyword search within filtered results:")
if search_query:
    # Highly performant vectorized search for filtered tables
    mask = df_filtered.astype(str).stack().str.contains(search_query, case=False).unstack().any(axis=1)
    df_final_display = df_filtered[mask]
else:
    df_final_display = df_filtered

st.dataframe(df_final_display, use_container_width=True)
