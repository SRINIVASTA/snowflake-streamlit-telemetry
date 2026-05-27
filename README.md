# 📊 Snowflake Live Data Engine & Telemetry Dashboard

An enterprise-grade, real-time analytics web dashboard built with **Streamlit** and powered by data streamed directly from **Snowflake Cloud Data Platform**. This application captures, filters, and maps out trending AI persona interactions and edge-telemetry log assets.

🚀 **Live Deployment URL:** [https://streamlit.io](https://app-app-telemetry-j8qfy9ank6wehuttph3guk.streamlit.app/)

---

## 🛠️ Tech Architecture Hierarchy

* **Data Cloud Core:** Snowflake Data Architecture (`trending_analytics_db.ai_telemetry.ai_agent_interactions`)
* **Compute Engine:** Snowflake Virtual Warehouse Engine (`COMPUTE_WH`)
* **Security & IAM Layers:** Dedicated service user segregation (`TRENDS_DEV_USER` assigned to `TRENDS_DATA_ROLE`)
* **Application Frontend Framework:** Streamlit Open-Source Cloud Engine Engine
* **Visual Processing Layout:** Interactive Altair Vector Maps

---

## 📊 Embedded System Architecture Map

```text
🌐 Global Organization Umbrella
 └── 🏢 Snowflake Account (ERCWFDH-AZ98278)
      └── 🗄️ Database (TRENDING_ANALYTICS_DB)
           └── 📁 Schema (AI_TELEMETRY)
                └── 📊 Data Table (AI_AGENT_INTERACTIONS) ---> Streamed Live to Streamlit UI
```

---

## 🚀 Key Functional Features

* **Interactive Multi-Axis Filtering:** Use the left-hand sidebar to seamlessly isolate telemetry metrics by **Region** and **Device Engine**.
* **Premium Intelligence Visual Maps:** High-fidelity, reactive bar charts and scatter plots tracking session distribution over custom time-series horizons.
* **Granular Text Querying Engine:** Real-time character pattern matcher to instantaneously filter thousands of logs over raw string values.
* **Encrypted Security Layering:** Employs Snowflake Python Connector bindings relying completely on server-side zero-leak environment configurations.

---

## ⚙️ Application Dependency Stack

Your repository workspace is maintained explicitly by the following structural manifest configurations:

### `requirements.txt`
```text
streamlit
snowflake-connector-python
pandas
```

---

## 🛡️ Administrative Deployment Security

This project relies entirely on modern production-grade secret practices. To deploy this pipeline yourself:
1. Initialize a blank workspace using **GitHub Web UI**.
2. Deploy the build via the **Streamlit Community Cloud console**.
3. Under **Advanced Settings -> Secrets**, safely inject your secure Snowflake cloud engine configurations using the explicit parameters below:

```toml
[snowflake]
user = "TRENDS_DEV_USER"
password = "YOUR_SECURE_PASSWORD"
account = "ERCWFDH-AZ98278"
warehouse = "COMPUTE_WH"
database = "TRENDING_ANALYTICS_DB"
schema = "AI_TELEMETRY"
```

---
👨‍💻 Maintained with care by [@srinivasta](https://github.com).
