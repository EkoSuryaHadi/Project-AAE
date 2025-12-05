# rcu_monitoring_dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import time

# === Metadata dari RCU2.xlsx ===
rcu_data = [
    ["101 F 501-502-504", "101-F-504", "PRESS FUEL GAS BURNER", "PG-148", 0.5, 3.5, "kg/cm²G"],
    ["101 F 501-502-504", "101-F-504", "PRESS FUEL OIL BURNER", "PG-147", 4, 12, "kg/cm²G"],
    ["101 F 501-502-504", "101-F-504", "TEMPERATURE FUEL OIL RETURN", "TG-110", 90, 130, "°C"],
    ["101 F 501-502-504", "101-F-504", "PRESS DIFF ATOMIZING STEAM", "PDI-153", 1, 3, "kg/cm²"],
    ["101 F 501-502-504", "101-F-504", "DRAFT KONVEKSI", "PG-159", -40, -5, "mm.H₂O"],
    ["101 F 501-502-504", "101-F-504", "DRAFT RADIANT / STACK", "PG-160", -15, -2, "mm.H₂O"],
    ["101 F 501-502-504", "101-F-504", "O2 ANALYZER", "AT-013", 1.5, 5, "%"],
    ["101 F 501-502-504", "101-V-514 (FG COB DFAH)", "KO DRUM LEVEL", "LG-M-217", 0, 80, "%"],
    ["101 F 501-502-504", "101-V-514 (FG COB DFAH)", "KO DRUM PRESSURE", "PG-254", 5.5, 7, "kg/cm²"],
    ["101 F 501-502-504", "101-V-514 (FG COB DFAH)", "PRESSURE DIFF. COALESCER", "PDG-305", 0.1, 1, "kg/cm²"],
    ["101 F 501-502-504", "101-V-514 (FG COB DFAH)", "FUEL GAS TEMP OUTLET E-503", "TG-287", 40, 80, "°C"],
    ["101 F 501-502-504", "101V-515 (FG F-504)", "KO DRUM LEVEL", "LG-M-219", 0, 65.2, "%"],
    ["101 F 501-502-504", "101V-515 (FG F-504)", "KO DRUM PRESSURE", "PG-255", 5.5, 7, "kg/cm²"],
    ["101 F 501-502-504", "101V-515 (FG F-504)", "PRESSURE DIFF. COALESCER", "PDG-306", 0.1, 1, "kg/cm²"],
    ["101 F 501-502-504", "101V-515 (FG F-504)", "FUEL GAS TEMP OUTLET E-504", "TG-272", 40, 80, "°C"],
    ["101 F 501-502-504", "BLOWDOWN SYSTEM", "LEVEL 101-V-533", "LG-M-215", 0, 80, "%"],
    ["101 F 501-502-504", "BLOWDOWN SYSTEM", "PRESS 101-V-533", "PG-250", 0.05, 0.5, "kg/cm²"],
]

df_meta = pd.DataFrame(rcu_data, columns=["SubEquipment", "System", "Parameter", "TagNo.", "Min", "Max", "Satuan"])
df_meta["TagNo."] = df_meta["TagNo."].str.strip()
tags = df_meta["TagNo."].tolist()

tag_to_min = df_meta.set_index("TagNo.")["Min"].to_dict()
tag_to_max = df_meta.set_index("TagNo.")["Max"].to_dict()
tag_to_unit = df_meta.set_index("TagNo.")["Satuan"].to_dict()
tag_to_desc = df_meta.set_index("TagNo.")["Parameter"].to_dict()

# === Simulasi data real-time ===
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
st.set_page_config(page_title="RCU Monitoring Dashboard", layout="wide")
st.title("🔥 RCU Monitoring Dashboard")
st.markdown("Simulasi real-time berdasarkan batas operasional dari RCU2.xlsx")

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
    st.metric("Waktu Terakhir", now.strftime("%H:%M:%S"))
with col2:
    st.metric("Total Parameter", len(tags))
with col3:
    st.metric("Anomali Terdeteksi", anomaly_count, delta_color="inverse")

# === Visualisasi: 1 baris ===
critical_tags = ["PG-148", "AT-013", "LG-M-219", "PG-160"]
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