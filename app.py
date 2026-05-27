import streamlit as st
import snowflake.connector
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Snowflake Telemetry Data Explorer", layout="wide")
st.title("📊 Snowflake Live Data Engine")

# 2. Establish Secure Connection to Snowflake Cloud Data Platform
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

# 3. Optimized Query Function with Streamlit Cache 
@st.cache_data(ttl=600)
def load_data(query):
    with conn.cursor() as cur:
        cur.execute(query)
        columns = [col[0] for col in cur.description] 
        return pd.DataFrame(cur.fetchall(), columns=columns)

# 4. Fetch Master Data
with st.spinner("Streaming data from Snowflake..."):
    sql_query = "SELECT * FROM trending_analytics_db.ai_telemetry.ai_agent_interactions LIMIT 1000;"
    df_master = load_data(sql_query)

# 5. LEFT SIDEBAR FILTERS (Controls everything below)
st.sidebar.header("🔍 Interactive Controls")

# Build unique filter lists dynamically from the data
geo_options = ["All Regions"] + sorted(df_master["GEO_LOCATION"].unique().tolist()) if "GEO_LOCATION" in df_master.columns else ["All Regions"]
device_options = ["All Devices"] + sorted(df_master["DEVICE_TYPE"].unique().tolist()) if "DEVICE_TYPE" in df_master.columns else ["All Devices"]

selected_geo = st.sidebar.selectbox("Select Region", geo_options)
selected_device = st.sidebar.selectbox("Select Device Type", device_options)

# Apply Sidebar Selections to Filter Data Dynamically
df_filtered = df_master.copy()

if selected_geo != "All Regions":
    df_filtered = df_filtered[df_filtered["GEO_LOCATION"] == selected_geo]

if selected_device != "All Devices":
    df_filtered = df_filtered[df_filtered["DEVICE_TYPE"] == selected_device]


# 6. VISUAL METRICS ROW (Updates based on sidebar)
col1, col2, col3 = st.columns(3)
col1.metric("Filtered Records", len(df_filtered))
if "SESSION_DURATION_SEC" in df_filtered.columns and len(df_filtered) > 0:
    col2.metric("Avg Session Duration", f"{int(df_filtered['SESSION_DURATION_SEC'].mean())}s")
else:
    col2.metric("Avg Session Duration", "0s")
    
if "AI_AGENT_ASSISTED" in df_filtered.columns and len(df_filtered) > 0:
    ai_pct = (df_filtered['AI_AGENT_ASSISTED'].astype(str).str.upper() == 'TRUE').mean() * 100
    col3.metric("AI Assisted Rate", f"{ai_pct:.1f}%")
else:
    col3.metric("AI Assisted Rate", "0.0%")

st.markdown("---")


# 7. TRENDING VISUAL MAPS (Placing charts first as requested)
st.subheader("📈 Trending Visual Intelligence Maps")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.write("**Activity Distribution by Region**")
    if "GEO_LOCATION" in df_filtered.columns and len(df_filtered) > 0:
        geo_counts = df_filtered["GEO_LOCATION"].value_counts()
        st.bar_chart(geo_counts)
    else:
        st.info("No regional data matches current filters.")

with chart_col2:
    st.write("**Access Methods by Device Type**")
    if "DEVICE_TYPE" in df_filtered.columns and len(df_filtered) > 0:
        device_counts = df_filtered["DEVICE_TYPE"].value_counts()
        st.bar_chart(device_counts)
    else:
        st.info("No device data matches current filters.")

st.markdown("---")


# 8. TELEMETRY DATA TABLE (Placing raw data at the bottom)
st.subheader("📋 Raw Telemetry Data Stream")

# Text search bar specifically for filtering the current table rows
search_query = st.text_input("🔍 Keyword search within filtered results:")
if search_query:
    mask = df_filtered.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
    df_final_display = df_filtered[mask]
else:
    df_final_display = df_filtered

st.dataframe(df_final_display, use_container_width=True)
