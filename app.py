import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF

# --- 1. LICENSE & SECURITY SYSTEM ---
MASTER_LICENSE_KEY = "PRO-MAX-200"

def validate_license(key):
    return key == MASTER_LICENSE_KEY

# --- 2. LOGIC FOR TEACHER & CLASS ---
def get_monthly_periods(value, unit):
    if unit == "Daily": return value * 26
    if unit == "Weekly": return value * 4
    return value

def get_status(m_periods):
    if m_periods < 40: return "🛑 Critical: Under-utilized", "Red"
    if m_periods > 120: return "🚨 Overload: High Burnout", "Red"
    return "✅ Efficient: Ideal Load", "Green"

# --- 3. PDF GENERATION LOGIC ---
def generate_report(school_name, p_val, s_val, c_val, overall):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="School Resource Optimization Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Institution: {school_name}", ln=True)
    pdf.cell(200, 10, txt=f"Report Date: {datetime.date.today()}", ln=True)
    pdf.ln(5)
    
    # Table Header
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "Section Name", 1)
    pdf.cell(90, 10, "Profit Level (1-200)", 1, ln=True)
    
    # Table Data
    pdf.set_font("Arial", size=12)
    data = {"Primary Section": p_val, "Secondary Section": s_val, "College Section": c_val}
    for sec, val in data.items():
        pdf.cell(100, 10, sec, 1)
        pdf.cell(90, 10, str(val), 1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"OVERALL PERFORMANCE SCORE: {overall} / 200", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 4. APP INTERFACE ---
st.set_page_config(page_title="Institutional Optimizer", layout="wide")

if 'auth' not in st.session_state:
    st.session_state.auth = False

# --- LOGIN SCREEN ---
if not st.session_state.auth:
    st.title("🔐 System Activation")
    school_input = st.text_input("Enter Institution Name")
    key_input = st.text_input("Enter License Key", type="password")
    if st.button("Activate System"):
        if validate_license(key_input):
            st.session_state.auth = True
            st.session_state.school = school_input
            st.rerun()
        else:
            st.error("Invalid License Key. Please enter 'PRO-MAX-200'")

# --- MAIN DASHBOARD ---
else:
    st.title(f"🏫 {st.session_state.school} - Dashboard")
    
    # Section Profit Levels (1-200)
    st.subheader("📊 Sectional Profit Levels")
    c1, c2, c3 = st.columns(3)
    with c1: p_lvl = st.number_input("Primary Level Profit", 1, 200, 85)
    with c2: s_lvl = st.number_input("Secondary Level Profit", 1, 200, 110)
    with c3: c_lvl = st.number_input("College Level Profit", 1, 200, 150)
    
    overall_score = int((p_lvl + s_lvl + c_lvl) / 3)
    st.markdown(f"### Overall Profit Score: **{overall_score} / 200**")
    st.progress(overall_score/200)

    # Teacher Calculator
    st.markdown("---")
    st.subheader("👨‍🏫 Dynamic Teacher Load Calculator")
    t1, t2, t3, t4 = st.columns(4)
    with t1: t_name = st.text_input("Teacher Name", "Staff 1")
    with t2: unit = st.selectbox("Unit", ["Daily", "Weekly", "Monthly"])
    with t3: val = st.number_input(f"Periods ({unit})", value=3)
    with t4:
        m_periods = get_monthly_periods(val, unit)
        advice, color = get_status(m_periods)
        st.write(f"Monthly Load: **{m_periods} Periods**")
        st.info(advice)

    # Export Report
    st.markdown("---")
    if st.button("Generate Final PDF Report"):
        try:
            report_bytes = generate_report(st.session_state.school, p_lvl, s_lvl, c_lvl, overall_score)
            st.download_button(
                label="📥 Download PDF Report",
                data=report_bytes,
                file_name=f"Report_{st.session_state.school}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error generating PDF: {e}")

    if st.sidebar.button("Log Out"):
        st.session_state.auth = False
        st.rerun()
