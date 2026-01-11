import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64

if "page" not in st.session_state:
    st.session_state.page = "home"

if "alarm_played_for" not in st.session_state:
    st.session_state.alarm_played_for = None


def play_hidden_audio(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    audio_html = f"""
    <audio autoplay style="display:none">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)


if st.session_state.page == "home":
    st.set_page_config(page_title="Sepsis Monitoring System", layout="centered")

    st.title("🩺 Early Sepsis Risk Monitoring")
    st.markdown(
        """
        Hospitals often miss early signs of patient deterioration  
        because vital changes happen gradually.

        This system helps **nurses and clinicians**  
        identify **high-risk patients early** using  
        simple, explainable clinical rules.
        """
    )

    st.markdown("### What this app does")
    st.write(
        """
        • qSOFA-based risk screening  
        • Time-series vital monitoring  
        • Clear alert escalation  
        • Decision-support (not diagnosis)  
        """
    )

    if st.button("▶ Open Monitoring Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()


if st.session_state.page == "dashboard":
    st.set_page_config(page_title="Sepsis Screening Dashboard", layout="wide")

    st.title("🩺 Sepsis Screening & Monitoring Dashboard")
    st.caption("⚠️ Rule-based screening tool. Supports clinical decision-making.")

    uploaded_file = st.file_uploader("Upload Sepsis CSV File (.csv)", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        required_cols = [
            "patient_id","age","gender","hour_from_admission",
            "respiratory_rate","systolic_bp","spo2_pct","heart_rate",
            "temperature_c","wbc_count","lactate","creatinine"
        ]

        if not all(col in df.columns for col in required_cols):
            st.error("Missing required columns in dataset")
            st.stop()

        df = df.sort_values(["patient_id","hour_from_admission"])

        df["gcs_proxy"] = 15
        df.loc[df["spo2_pct"] < 92, "gcs_proxy"] = 13
        df.loc[(df["spo2_pct"] < 90) & (df["heart_rate"] > 120), "gcs_proxy"] = 12
        df["mental_status"] = (df["gcs_proxy"] < 15).astype(int)

        df["qSOFA"] = 0
        df.loc[df["respiratory_rate"] >= 22, "qSOFA"] += 1
        df.loc[df["systolic_bp"] <= 100, "qSOFA"] += 1
        df.loc[df["mental_status"] == 1, "qSOFA"] += 1

        df["Alert"] = df["qSOFA"].map({
            0: "🟢 Low Risk",
            1: "🟠 Moderate Risk",
            2: "🔴 High Risk",
            3: "🔴 High Risk"
        })

        st.subheader("👤 Patient Selection")
        patient_id = st.selectbox("Select Patient ID", df["patient_id"].unique())
        patient_df = df[df["patient_id"] == patient_id]
        latest = patient_df.iloc[-1]

        st.subheader("🧾 Patient Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Patient ID", patient_id)
        c2.metric("Age", patient_df["age"].iloc[0])
        c3.metric("Gender", patient_df["gender"].iloc[0])

        lab_items = {
            "WBC": latest["wbc_count"],
            "Lactate": latest["lactate"],
            "Creatinine": latest["creatinine"],
            "Temp (°C)": latest["temperature_c"],
            "SpO₂ (%)": latest["spo2_pct"]
        }

        dropdown = ["Latest Lab Result"] + [f"{k} - {v:.2f}" for k, v in lab_items.items()]
        c4.selectbox("Latest Lab Result", dropdown, label_visibility="collapsed")

        st.subheader("🚨 Current Risk Status")
        r1, r2 = st.columns(2)
        r1.metric("qSOFA Score", int(latest["qSOFA"]))

        if latest["qSOFA"] >= 2:
            r2.error("🔴 HIGH SEPSIS RISK")
            if st.session_state.alarm_played_for != patient_id:
                play_hidden_audio("alarm_21s.mp3")
                st.session_state.alarm_played_for = patient_id
        elif latest["qSOFA"] == 1:
            r2.warning("🟠 MODERATE RISK")
            st.session_state.alarm_played_for = None
        else:
            r2.success("🟢 LOW RISK")
            st.session_state.alarm_played_for = None

        st.subheader("📊 Patient Time-Series Data")
        st.dataframe(patient_df)

        st.subheader("📈 Vital Signs (Compact View)")
        fig, ax = plt.subplots(figsize=(6,3))
        ax.plot(patient_df["hour_from_admission"], patient_df["respiratory_rate"], marker="o", label="RR")
        ax.plot(patient_df["hour_from_admission"], patient_df["systolic_bp"], marker="o", label="SBP")
        ax.axhline(22, linestyle="--")
        ax.axhline(100, linestyle="--")
        ax.legend(fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)