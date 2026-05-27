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

import matplotlib.pyplot as plt

# 1. Create a standard Matplotlib figure
fig, ax = plt.subplots()
df["USER_PERSONA"].value_counts().plot(kind="bar", ax=ax)

# 2. Render it inside your Streamlit app
st.pyplot(fig)

# Create a sidebar navigation panel
st.sidebar.header("🔍 Global Data Filters")

# Extract unique values for filtering
available_personas = ["All"] + sorted(df["USER_PERSONA"].unique().tolist())
available_devices = ["All"] + sorted(df["DEVICE_TYPE"].unique().tolist())

# Create the visual dropdown selectors
selected_persona = st.sidebar.selectbox("Filter by User Persona", available_personas)
selected_device = st.sidebar.selectbox("Filter by Device Type", available_devices)

# Apply filters dynamically to the dataframe
filtered_df = df.copy()
if selected_persona != "All":
    filtered_df = filtered_df[filtered_df["USER_PERSONA"] == selected_persona]
if selected_device != "All":
    filtered_df = filtered_df[filtered_df["DEVICE_TYPE"] == selected_device]

st.subheader("📈 Trending Visual Intelligence Maps")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.write("**Top Interacting AI Personas**")
    # Interactive Altair Bar Chart with tooltips
    st.altair_chart(
        alt.Chart(filtered_df).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
            x=alt.X('USER_PERSONA:N', title='User Persona', sort='-y'),
            y=alt.Y('count():Q', title='Total Interactions'),
            color=alt.Color('USER_PERSONA:N', legend=None),
            tooltip=['USER_PERSONA', 'count()']
        ).interactive(), 
        use_container_width=True
    )

with chart_col2:
    st.write("**Session Duration Insights by Device**")
    # Interactive Scatter Plot
    st.altair_chart(
        alt.Chart(filtered_df).mark_circle(size=60).encode(
            x='EVENT_TIMESTAMP:T',
            y='SESSION_DURATION_SEC:Q',
            color='DEVICE_TYPE:N',
            tooltip=['USER_PERSONA', 'DEVICE_TYPE', 'SESSION_DURATION_SEC']
        ).interactive(),
        use_container_width=True
    )
