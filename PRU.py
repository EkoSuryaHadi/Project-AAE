# pru_monitoring_dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import time

# === 1. Muat data PRU dari file ===
pru_data = [
    ["104 K 501", "104-K-501 HPC", "COMP. SUCT PRESS", "PI 127", 10.00, 14.00, "KG/CM2"],
    ["104 K 501", "104-K-501 HPC", "∆P.CONTROL OIL FILTER", "PDT 621", 0.05, 1.00, "KG/CM2"],
    ["104 K 501", "104-K-501 HPC", "COMP. DISCH PRESS", "PI 128", 18.00, 19.40, "KG/CM2"],
    ["104 K 501", "104-K-501 HPC", "COMP. DISCH TEMP", "TI 017", 49.00, 55.30, "oC"],
    ["104 K 501", "104-K-501 HPC", "COMP. SUCT DRUM PRESS", "PG-013", 10.00, 14.00, "KG/CM2"],
    ["104 K 501", "104-K-501 HPC", "EXTERNAL N2 GAS PRESS", "PG-612", 3.20, 4.00, "KG/CM2"],
    ["104 K 501", "104-K-501 HPC", "∆P PRIMARY SEAL GAS FILTER", "PDG-013", 0.20, 0.70, "KG/CM2"],
    ["104 K 501", "104-K-501 HPC", "PRIMARY BUFFER SUPPLY PRESS", "PG-611", 16.99, 18.27, "KG/CM2"],
    ["104 K 501", "104-K-501 HPC", "FLUSH GAS SUPPLY PRESS", "PG-610", 18.00, 19.38, "KG/CM2"],
    ["104 K 501", "104-K-501 HPC", "PRIMARY SEAL VENT DIFF. PRESSURE", "PDT 607", 0.02, 1.57, "KG/CM2"],
    ["104 K 501", "104-K-501 HPC", "∆P. PRIMARY BUFFER-FLUSH GAS", "PDI-604", 0.00, 0.70, "KG/CM2"],
    ["104 K 501", "104-K-501 HPC", "OIL RESERVOIR LEVEL", "LG 670", 50.00, 100.00, "%"],
    ["104 K 501", "104-K-501 HPC", "OIL RESERVOIR TEMP", "TG 670", 65.00, 90.00, "oC"],
    ["104 K 501", "104-K-501 HPC", "L.O OUTLET COOLER TEMP", "TG 674", 46.00, 61.50, "oC"],
    ["104 K 501", "104-K-501 HPC", "CWR OIL COOLER TEMP.", "TG 672/673", 37.00, 41.00, "oC"],
    ["104 K 501", "104-K-501 HPC", "∆P OIL FILTER", "PDI 662", 0.05, 1.00, "KG/CM2"],
    ["104 K 501", "104-K-501 HPC", "OUTLET OIL FILTER PRESS.", "PG 672", 11.00, 12.00, "KG/CM2"],
    ["104 K 501", "104-K-501 HPC", "L.O SUPPLY PRESS", "PT 600", 1055.00, 1266.00, "KG/CM2"],  # Akan diperbaiki
    ["104 K 501", "104-K-501 HPC", "L.O CONTROL OIL SUPPLY PRESS", "PG 674", 7.91, 10.7, "KG/CM2"],
    ["104 K 501", "104-K-501 HPC", "L.O RUNDOWN TANK LEVEL", "LG 610", 50.00, 100.00, "%"],
    ["104 K 501", "104-K-501 HPC", "L.O RTRN O/B (TURBINE) TEMP", "TG 631", 50.00, 82.00, "oC"],
    ["104 K 501", "104-K-501T-P1 (TURBINE)", "STEAM INLET PRESS", "PG 675", 16.00, 20.00, "KG/CM2"],
    ["104 K 501", "104-K-501T-P1 (TURBINE)", "STEAM INLET TEMP.", "TG 675", 300.00, 370.00, "oC"],
    ["104 K 501", "104-K-501T-P1 (TURBINE)", "SUCT PRESS", "PG 670", -1, 1.5, "KG/CM2"],
    ["104 K 501", "104-K-501T-P1 (TURBINE)", "PRESS DISCHARGE", "PI 660", 13.00, 15.5, "KG/CM2"],
    ["104 K 501", "104-K-501T-P1 (TURBINE)", "SPEED TURBINE", "SI 660", 1258.00, 1554.00, "RPM"],
    ["104 K 501", "104-K-501-T TURBINE", "HP STEAM INLET PRESS", "PI-029", 39.00, 44.00, "KG/CM2"],
    ["104 K 501", "104-K-501-T TURBINE", "HP STEAM INLET TEMP", "TI 011", 350.00, 370.00, "oC"],
    ["104 K 501", "104-K-501-T TURBINE", "TURBINE SPEED", "SC-621", 6210.00, 9316.00, "RPM"],
    ["104 K 501", "HPC SURF. CONDENSER", "SURF COND. LEVEL", "LG-690", 276.00, 1070.00, "MM"],
    ["104 K 501", "HPC SURF. CONDENSER", "SURF COND. VACUUM PRESS", "PG 032", -0.904, -0.87, "KG/CM2"],
    ["104 K 501", "HPC SURF. CONDENSER", "MPS EJECTOR SYSTEM 1 PRESS", "PG-691/692", 16.00, 22.00, "KG/CM2"],
    ["104 K 501", "POMPA 104-P-505 A", "PRESS DISCHARGE", "DISCH-A", None, 7.80, "KG/CM2"],
    ["104 K 501", "POMPA 104-P-505 B", "PRESS DISCHARGE", "DISCH-B", None, 7.80, "KG/CM2"],
]

# Buat DataFrame
df_raw = pd.DataFrame(pru_data, columns=["ParentSystem", "System", "Parameter", "TagNo.", "Min", "Max", "Satuan"])

# Normalisasi TagNo: ganti spasi dengan strip, hapus trailing spaces
df_raw["TagNo."] = df_raw["TagNo."].astype(str).str.replace(" ", "-").str.strip()
df_raw = df_raw[df_raw["TagNo."] != "nan"].copy()

# Perbaiki L.O SUPPLY PRESS (typo satuan)
df_raw.loc[df_raw["TagNo."] == "PT-600", ["Min", "Max"]] = [10.55, 12.66]

# Normalisasi satuan: oC → °C, KG/CM2 → kg/cm²
df_raw["Satuan"] = df_raw["Satuan"].str.replace("oC", "°C").str.replace("KG/CM2", "kg/cm²").str.replace("MM", "mm")

# Konversi Min/Max ke numerik
df_raw["Min"] = pd.to_numeric(df_raw["Min"], errors="coerce")
df_raw["Max"] = pd.to_numeric(df_raw["Max"], errors="coerce")

# Ganti None/NaN dengan -inf/+inf untuk aturan deteksi
df_meta = df_raw.copy()
df_meta["Min"] = df_meta["Min"].fillna(-np.inf)
df_meta["Max"] = df_meta["Max"].fillna(np.inf)

# Siapkan lookup dictionary
tags = df_meta["TagNo."].tolist()
tag_to_min = df_meta.set_index("TagNo.")["Min"].to_dict()
tag_to_max = df_meta.set_index("TagNo.")["Max"].to_dict()
tag_to_unit = df_meta.set_index("TagNo.")["Satuan"].to_dict()
tag_to_desc = df_meta.set_index("TagNo.")["Parameter"].to_dict()

# === 2. Fungsi simulasi data real-time ===
def simulate_current_data():
    data = {}
    for tag in tags:
        vmin = tag_to_min[tag]
        vmax = tag_to_max[tag]
        if np.isinf(vmin) and np.isinf(vmax):
            val = 0
        elif np.isinf(vmin):
            # Hanya punya max → jangan melebihi max
            val = np.random.uniform(vmax * 0.6, vmax * 1.1)
        elif np.isinf(vmax):
            # Hanya punya min → jangan di bawah min
            val = np.random.uniform(vmin * 0.9, vmin * 1.4)
        else:
            mid = (vmin + vmax) / 2
            span = (vmax - vmin) / 2
            val = np.random.normal(loc=mid, scale=span / 4)
        # Sisipkan anomali acak (5%)
        if np.random.rand() < 0.05:
            if np.isinf(vmin):
                val = vmax + np.random.uniform(0.5, 1.5)
            elif np.isinf(vmax):
                val = vmin - np.random.uniform(0.5, 1.5)
            else:
                if np.random.rand() < 0.5:
                    val = vmin - np.random.uniform(0.2, 1)
                else:
                    val = vmax + np.random.uniform(0.2, 1)
        data[tag] = round(float(val), 2)
    return data

# === 3. Streamlit UI ===
st.set_page_config(page_title="PRU Monitoring Dashboard", layout="wide")
st.title("⚙️ PRU Monitoring Dashboard")
st.markdown("Simulasi real-time berdasarkan batas operasional dari PRU.xlsx")

# Inisialisasi histori
if "history" not in st.session_state:
    st.session_state.history = []

# Simulasi data terbaru
now = datetime.now()
new_data = simulate_current_data()
new_data["timestamp"] = now
st.session_state.history.append(new_data)

# Simpan hanya 12 jam terakhir
if len(st.session_state.history) > 12:
    st.session_state.history = st.session_state.history[-12:]

df_hist = pd.DataFrame(st.session_state.history)

# Hitung jumlah anomali
anomaly_count = 0
for tag in tags:
    val = new_data[tag]
    vmin, vmax = tag_to_min[tag], tag_to_max[tag]
    is_anom = False
    if np.isinf(vmin) and not np.isinf(vmax):
        is_anom = val > vmax
    elif not np.isinf(vmin) and np.isinf(vmax):
        is_anom = val < vmin
    elif not np.isinf(vmin) and not np.isinf(vmax):
        is_anom = (val < vmin) or (val > vmax)
    if is_anom:
        anomaly_count += 1

# Ringkasan
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Waktu", now.strftime("%H:%M:%S"))
with col2:
    st.metric("Parameter", len(tags))
with col3:
    st.metric("Anomali", anomaly_count, delta_color="inverse")

# === 4. Visualisasi 1 baris ===
critical_tags = ["PI-128", "TI-017", "PT-600", "SC-621"]  # Discharge P/T, Lube Oil P, Turbine Speed
valid_tags = [t for t in critical_tags if t in tags]

if valid_tags and len(df_hist) > 1:
    st.subheader("📈 Tren Parameter Kritis (12 Jam Terakhir)")
    fig, axes = plt.subplots(1, len(valid_tags), figsize=(4 * len(valid_tags), 3))
    if len(valid_tags) == 1:
        axes = [axes]
    for i, tag in enumerate(valid_tags):
        ax = axes[i]
        ax.plot(df_hist["timestamp"], df_hist[tag], marker="o", linewidth=1.5, color="steelblue")
        vmin, vmax = tag_to_min[tag], tag_to_max[tag]
        if not np.isinf(vmin):
            ax.axhline(vmin, color="green", linestyle="--", alpha=0.7, label="Min")
        if not np.isinf(vmax):
            ax.axhline(vmax, color="red", linestyle="--", alpha=0.7, label="Max")
        ax.set_title(f"{tag}\n{tag_to_desc[tag]}", fontsize=9)
        ax.set_ylabel(tag_to_unit[tag], fontsize=8)
        ax.tick_params(axis='x', rotation=30, labelsize=7)
        ax.tick_params(axis='y', labelsize=7)
        ax.grid(True, linestyle=":", alpha=0.5)
        if not np.isinf(vmin) or not np.isinf(vmax):
            ax.legend(fontsize=7)
    plt.tight_layout()
    st.pyplot(fig)

# === 5. Tabel Detail Semua Parameter ===
st.subheader("📋 Status Semua Parameter Saat Ini")
rows = []
for tag in tags:
    val = new_data[tag]
    vmin, vmax = tag_to_min[tag], tag_to_max[tag]
    if np.isinf(vmin) and np.isinf(vmax):
        status = "Normal"
    elif np.isinf(vmin):
        status = "Anomali" if val > vmax else "Normal"
    elif np.isinf(vmax):
        status = "Anomali" if val < vmin else "Normal"
    else:
        status = "Anomali" if (val < vmin or val > vmax) else "Normal"
    rows.append({
        "Tag": tag,
        "Parameter": tag_to_desc[tag],
        "Nilai": val,
        "Satuan": tag_to_unit[tag],
        "Rentang": f"{vmin if not np.isinf(vmin) else '-inf'} – {vmax if not np.isinf(vmax) else 'inf'}",
        "Status": "🔴 Anomali" if status == "Anomali" else "🟢 Normal"
    })

df_table = pd.DataFrame(rows)
st.dataframe(df_table, use_container_width=True, hide_index=True)

# === 6. Auto-refresh ===
st.markdown("---")
st.markdown("🔁 Memperbarui otomatis setiap 5 detik...")
time.sleep(5)
if hasattr(st, "rerun"):
    st.rerun()
else:
    st.experimental_rerun()