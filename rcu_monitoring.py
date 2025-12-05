# rcu_monitoring_dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import time

# === 1. Baca Metadata dari RCU2.xlsx (disalin langsung) ===
data = [
    ["101 F 501-502-504", "101-F-504", "PRESS FUEL GAS BURNER", "PG-148", 0.5, 3.5, "kg/cm2G"],
    ["101 F 501-502-504", "101-F-504", "PRESS FUEL OIL BURNER", "PG-147", 4, 12, "kg/cm2G"],
    ["101 F 501-502-504", "101-F-504", "TEMPERATURE FUEL OIL RETURN", "TG-110", 90, 130, "°C"],
    ["101 F 501-502-504", "101-F-504", "PRESS DIFF ATOMIZING STEAM", "PDI-153", 1, 3, "kg/cm2"],
    ["101 F 501-502-504", "101-F-504", "DRAFT KONVEKSI", "PG-159", -40, -5, "mm.H2O"],
    ["101 F 501-502-504", "101-F-504", "DRAFT RADIANT / STACK", "PG-160", -15, -2, "mm.H2O"],
    ["101 F 501-502-504", "101-F-504", "O2 ANALYZER", "AT-013", 1.5, 5, "%"],
    ["101 F 501-502-504", "101-V-514 (FG COB DFAH)", "KO DRUM LEVEL", "LG-M-217", 0, 80, "%"],
    ["101 F 501-502-504", "101-V-514 (FG COB DFAH)", "KO DRUM PRESSURE", "PG-254", 5.5, 7, "kg/cm2"],
    ["101 F 501-502-504", "101-V-514 (FG COB DFAH)", "LEVEL COALESCER A-526", "LG-M-218A", 0, 80, "%"],
    ["101 F 501-502-504", "101-V-514 (FG COB DFAH)", "LEVEL COALESCER A-526", "LG-M-218B", 0, 80, "%"],
    ["101 F 501-502-504", "101-V-514 (FG COB DFAH)", "PRESSURE DIFF. COALESCER", "PDG-305", 0.1, 1, "kg/cm2"],
    ["101 F 501-502-504", "101-V-514 (FG COB DFAH)", "FUEL GAS TEMP OUTLET E-503", "TG-287", 40, 80, "°C"],
    ["101 F 501-502-504", "101V-515 (FG F-504)", "KO DRUM LEVEL", "LG-M-219", 0, 65.2, "%"],
    ["101 F 501-502-504", "101V-515 (FG F-504)", "KO DRUM PRESSURE", "PG-255", 5.5, 7, "kg/cm2"],
    ["101 F 501-502-504", "101V-515 (FG F-504)", "LEVEL COALESCER A-527", "LG-M-220A", 0, 80, "%"],
    ["101 F 501-502-504", "101V-515 (FG F-504)", "LEVEL COALESCER A-527", "LG-M-220B", 0, 80, "%"],
    ["101 F 501-502-504", "101V-515 (FG F-504)", "PRESSURE DIFF. COALESCER", "PDG-306", 0.1, 1, "kg/cm2"],
    ["101 F 501-502-504", "101V-515 (FG F-504)", "FUEL GAS TEMP OUTLET E-504", "TG-272", 40, 80, "°C"],
    ["101 F 501-502-504", "BLOWDOWN SYSTEM", "LEVEL 101-V-533", "LG-M-215", 0, 80, "%"],
    ["101 F 501-502-504", "BLOWDOWN SYSTEM", "LEVEL 101-V-534", "LG-M-216", 0, 80, "%"],
    ["101 F 501-502-504", "BLOWDOWN SYSTEM", "PRESS 101-V-533", "PG-250", 0.05, 0.5, "kg/cm2"],
]

# Buat DataFrame
df_raw = pd.DataFrame(data, columns=["SubEquipment", "System", "Parameter", "TagNo.", "Min", "Max", "Satuan"])

# Filter hanya yang punya TagNo. dan nilai numerik (bukan N/A)
df_meta = df_raw.dropna(subset=["TagNo."]).copy()
df_meta["Min"] = pd.to_numeric(df_meta["Min"], errors="coerce")
df_meta["Max"] = pd.to_numeric(df_meta["Max"], errors="coerce")
df_meta = df_meta.dropna(subset=["Min", "Max"])

# Buat lookup dictionaries
tag_to_min = df_meta.set_index("TagNo.")["Min"].to_dict()
tag_to_max = df_meta.set_index("TagNo.")["Max"].to_dict()
tag_to_unit = df_meta.set_index("TagNo.")["Satuan"].to_dict()
tag_to_desc = df_meta.set_index("TagNo.")["Parameter"].to_dict()
tags = df_meta["TagNo."].tolist()

# === 2. Simulasi Data Real-Time ===
def simulate_current_data():
    data = {}
    for tag in tags:
        vmin, vmax = tag_to_min[tag], tag_to_max[tag]
        mid = (vmin + vmax) / 2
        span = (vmax - vmin) / 2
        val = np.random.normal(loc=mid, scale=span / 4)
        # Sisipkan anomali acak (5% chance)
        if np.random.rand() < 0.05:
            if np.random.rand() < 0.5:
                val = vmin - np.random.uniform(0.1, 1.0)
            else:
                val = vmax + np.random.uniform(0.1, 1.0)
        data[tag] = round(float(val), 2)
    return data

# === 3. Streamlit App ===
st.set_page_config(page_title="RCU Monitoring Dashboard", layout="wide")
st.title("🔥 RCU Monitoring Dashboard")
st.markdown("Simulasi real-time berdasarkan batas operasional dari RCU2.xlsx")

# Inisialisasi histori
if "history" not in st.session_state:
    st.session_state.history = []

# Tambahkan data terbaru
current_time = datetime.now()
new_data = simulate_current_data()
new_data["timestamp"] = current_time
st.session_state.history.append(new_data)

# Simpan hanya 12 jam terakhir
if len(st.session_state.history) > 12:
    st.session_state.history = st.session_state.history[-12:]

df_hist = pd.DataFrame(st.session_state.history)

# Hitung anomali
anomaly_count = 0
for tag in tags:
    val = new_data[tag]
    if val < tag_to_min[tag] or val > tag_to_max[tag]:
        anomaly_count += 1

# === 4. Tampilan Ringkasan ===
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Waktu Terakhir", current_time.strftime("%H:%M:%S"))
with col2:
    st.metric("Total Parameter", len(tags))
with col3:
    st.metric("Anomali Terdeteksi", anomaly_count, delta_color="inverse")

# === 5. Visualisasi Grafik (4 Parameter Kunci) ===
key_tags = ["PG-148", "AT-013", "LG-M-219", "PG-160"]
valid_key_tags = [t for t in key_tags if t in tags]

if valid_key_tags and len(df_hist) > 1:
    st.subheader("📈 Trend Parameter Kritis (12 Jam Terakhir)")
    n = len(valid_key_tags)
    cols = 2 if n > 1 else 1
    rows = (n + 1) // 2 if n > 1 else 1
    fig, axes = plt.subplots(rows, cols, figsize=(12, 2.5 * rows))
    if n == 1:
        axes = [axes]
    else:
        axes = axes.flatten() if n > 2 else axes

    for i, tag in enumerate(valid_key_tags):
        ax = axes[i]
        ax.plot(df_hist["timestamp"], df_hist[tag], marker="o", linewidth=2, color="steelblue")
        ax.axhline(tag_to_min[tag], color="green", linestyle="--", alpha=0.7, label="Min")
        ax.axhline(tag_to_max[tag], color="red", linestyle="--", alpha=0.7, label="Max")
        ax.set_title(f"{tag} – {tag_to_desc[tag]}")
        ax.set_ylabel(tag_to_unit.get(tag, ""))
        ax.legend(loc="upper right")
        ax.grid(True, linestyle=":", alpha=0.5)
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    plt.tight_layout()
    st.pyplot(fig)

# === 6. Tabel Detail Status Semua Parameter ===
st.subheader("📋 Status Parameter Saat Ini")
detail_rows = []
for tag in tags:
    val = new_data[tag]
    vmin, vmax = tag_to_min[tag], tag_to_max[tag]
    status = "Anomali" if val < vmin or val > vmax else "Normal"
    detail_rows.append({
        "Tag": tag,
        "Parameter": tag_to_desc[tag],
        "Nilai": val,
        "Satuan": tag_to_unit[tag],
        "Rentang": f"{vmin} – {vmax}",
        "Status": "🔴 Anomali" if status == "Anomali" else "🟢 Normal"
    })

df_detail = pd.DataFrame(detail_rows)
st.dataframe(df_detail, use_container_width=True, hide_index=True)

# === 7. Auto-refresh ===
st.markdown("---")
st.markdown("🔁 Memperbarui otomatis setiap 5 detik...")

# Gunakan experimental_rerun untuk kompatibilitas versi lama
time.sleep(5)
if hasattr(st, "rerun"):
    st.rerun()
else:
    st.experimental_rerun()