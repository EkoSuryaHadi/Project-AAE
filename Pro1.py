# pro_monitoring_dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import time

# === Metadata dari PRO.xlsx ===
pro_data = [
    ["101 K 501", "101-K-501 (MAB) Turbine", "HP STEAM INLET PRESSURE", "PI-626", 40.00, 43.00, "kg/cm²G"],
    ["101 K 501", "101-K-501 (MAB) Turbine", "HP STEAM INLET TEMPERATURE", "TI-626", 375.00, 395.00, "°C"],
    ["101 K 501", "101-K-501 (MAB) Turbine", "EXHAUST STEAM TEMPERATURE", "TI-630", 40, 52, "°C"],
    ["101 K 501", "101-K-501 (MAB) Turbine", "TURBINE SPEED", "SC-625", 3600, 4200, "RPM"],
    ["101 K 501", "101-K-501 (MAB) Compressor", "PRESS. SUCTION COMPRESSOR", "PI-004", 0.00, 0.05, "kg/cm²G"],
    ["101 K 501", "101-K-501 (MAB) Compressor", "TEMP. SUCTION COMPRESSOR", "TI-007", 27.00, 35.00, "°C"],
    ["101 K 501", "101-K-501 (MAB) Compressor", "PRESS. DISCH. COMPRESSOR", "PG-005", 2.21, 3.28, "kg/cm²G"],
    ["101 K 501", "101-K-501 (MAB) Compressor", "TEMP. DISCH. COMPRESSOR", "TI-002", 164.00, 209.50, "°C"],
    ["101 K 501", "101-K-501 (LUBE OIL)", "LEVEL LUBE OIL RESERVOIR", "LG-601", 50.00, 100.00, "%"],
    ["101 K 501", "101-K-501 (LUBE OIL)", "PRESS. L/O SUPPLY", "PG-608", 3.1, 9.1, "kg/cm²G"],
    ["101 K 501", "SURFACE CONDENSER", "SURFACE CONDENSER LEVEL", "LI-653", 40.00, 60.00, "%"],
    ["101 K 501", "101-K-501T-P2 (MOTOR)", "DISCHARGE PRESS", "PI-661", 15.00, 18.40, "kg/cm²G"],
]

# Filter hanya yang punya TagNo. valid dan perbaiki typo
df_meta = pd.DataFrame(pro_data, columns=["SubEquipment", "System", "Parameter", "TagNo.", "Min", "Max", "Satuan"])
df_meta["TagNo."] = df_meta["TagNo."].str.strip().str.replace(" ", "-")
df_meta = df_meta[df_meta["TagNo."] != "N/A"].dropna(subset=["Min", "Max"])

# Perbaiki PRESS DISCHARGE jika ada
mask = df_meta["Parameter"] == "PRESS DISCHARGE"
if mask.any():
    row = df_meta[mask].iloc[0]
    if row["Min"] > row["Max"]:
        df_meta.loc[mask, ["Min", "Max"]] = [row["Max"], row["Min"]]

tags = df_meta["TagNo."].tolist()
tag_to_min = df_meta.set_index("TagNo.")["Min"].to_dict()
tag_to_max = df_meta.set_index("TagNo.")["Max"].to_dict()
tag_to_unit = df_meta.set_index("TagNo.")["Satuan"].to_dict()
tag_to_desc = df_meta.set_index("TagNo.")["Parameter"].to_dict()

# === Simulasi data ===
def simulate_current_data():
    data = {}
    for tag in tags:
        vmin, vmax = tag_to_min[tag], tag_to_max[tag]
        mid = (vmin + vmax) / 2
        span = (vmax - vmin) / 2
        val = np.random.normal(loc=mid, scale=span / 4)
        if np.random.rand() < 0.05:
            val = vmin - np.random.uniform(0.2, 1) if np.random.rand() < 0.5 else vmax + np.random.uniform(0.2, 1)
        data[tag] = round(float(val), 2)
    return data

# === Streamlit App ===
st.set_page_config(page_title="PRO Monitoring Dashboard", layout="wide")
st.title("⚙️ PRO (Production) Monitoring Dashboard")
st.markdown("Simulasi real-time berdasarkan PRO.xlsx")

if "history" not in st.session_state:
    st.session_state.history = []

now = datetime.now()
new_data = simulate_current_data()
new_data["timestamp"] = now
st.session_state.history.append(new_data)
if len(st.session_state.history) > 12:
    st.session_state.history = st.session_state.history[-12:]

df_hist = pd.DataFrame(st.session_state.history)

anomaly_count = sum(1 for tag in tags if new_data[tag] < tag_to_min[tag] or new_data[tag] > tag_to_max[tag])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Waktu", now.strftime("%H:%M:%S"))
with col2:
    st.metric("Parameter", len(tags))
with col3:
    st.metric("Anomali", anomaly_count, delta_color="inverse")

# === Visualisasi 1 baris ===
critical_tags = ["PI-626", "TI-002", "LG-601", "PG-005"]
valid_tags = [t for t in critical_tags if t in tags]

if valid_tags and len(df_hist) > 1:
    st.subheader("📈 Tren Parameter Kritis (12 Jam Terakhir)")
    fig, axes = plt.subplots(1, len(valid_tags), figsize=(4 * len(valid_tags), 3))
    if len(valid_tags) == 1:
        axes = [axes]
    for i, tag in enumerate(valid_tags):
        ax = axes[i]
        ax.plot(df_hist["timestamp"], df_hist[tag], marker="o", linewidth=1.5, color="steelblue")
        ax.axhline(tag_to_min[tag], color="green", linestyle="--", alpha=0.7)
        ax.axhline(tag_to_max[tag], color="red", linestyle="--", alpha=0.7)
        ax.set_title(f"{tag}\n{tag_to_desc[tag]}", fontsize=9)
        ax.set_ylabel(tag_to_unit[tag], fontsize=8)
        ax.tick_params(axis='x', rotation=30, labelsize=7)
        ax.tick_params(axis='y', labelsize=7)
        ax.grid(True, linestyle=":", alpha=0.5)
    plt.tight_layout()
    st.pyplot(fig)

# === Tabel Detail ===
st.subheader("📋 Status Semua Parameter Saat Ini")
rows = []
for tag in tags:
    val = new_data[tag]
    vmin, vmax = tag_to_min[tag], tag_to_max[tag]
    status = "Anomali" if val < vmin or val > vmax else "Normal"
    rows.append({
        "Tag": tag,
        "Parameter": tag_to_desc[tag],
        "Nilai": val,
        "Satuan": tag_to_unit[tag],
        "Rentang": f"{vmin} – {vmax}",
        "Status": "🔴 Anomali" if status == "Anomali" else "🟢 Normal"
    })
df_table = pd.DataFrame(rows)
st.dataframe(df_table, use_container_width=True, hide_index=True)

# === Auto-refresh ===
st.markdown("---")
st.markdown("🔁 Memperbarui otomatis setiap 5 detik...")
time.sleep(5)
if hasattr(st, "rerun"):
    st.rerun()
else:
    st.experimental_rerun()