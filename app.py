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

# 3. Optimized Query Function with Streamlit Cache (Prevents constant reloading)
@st.cache_data(ttl=600)
def load_data(query):
    with conn.cursor() as cur:
        cur.execute(query)
        columns = [col[0] for col in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=columns)

# 4. Fetch the Data
with st.spinner("Streaming data from Snowflake..."):
    # Replace this query with your exact table name from the previous step
    sql_query = "SELECT * FROM trending_analytics_db.ai_telemetry.ai_agent_interactions LIMIT 1000;"
    df = load_data(sql_query)

# 5. User Interface Controls & Advanced Processing
st.subheader("💡 Interactive Analytics Processing")

# Add a metric row
col1, col2, col3 = st.columns(3)
col1.metric("Total Streamed Rows", len(df))
if "SESSION_DURATION_SEC" in df.columns:
    col2.metric("Avg Session Duration", f"{int(df['SESSION_DURATION_SEC'].mean())}s")
if "AI_AGENT_ASSISTED" in df.columns:
    ai_pct = (df['AI_AGENT_ASSISTED'].astype(str).str.upper() == 'TRUE').mean() * 100
    col3.metric("AI Assisted Rate", f"{ai_pct:.1f}%")

st.markdown("---")

# Add interactive search box for your massive log
search_query = st.text_input("🔍 Filter rows by keyword (Persona, Device, Location, etc.):")
if search_query:
    # Scan all columns for text match
    mask = df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
    filtered_df = df[mask]
else:
    filtered_df = df

# Display clean interactive table layout
st.dataframe(filtered_df, use_container_width=True)
