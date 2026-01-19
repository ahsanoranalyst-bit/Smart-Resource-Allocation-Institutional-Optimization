import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF

# --- 1. SYSTEM CALCULATIONS ---
def get_monthly_periods(value, unit):
    if unit == "Daily": return value * 26
    if unit == "Weekly": return value * 4
    return value

def get_status(m_periods):
    if m_periods < 40: return "🛑 Critical: Under-utilized", 1
    if m_periods > 120: return "🚨 Overload: High Burnout", 2
    return "✅ Efficient: Ideal Load", 3

# --- 2. IMPROVED PDF GENERATION ---
def generate_institutional_report(school_name, sections_data, overall_profit):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Smart Institutional Optimization Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Institution: {school_name}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Date: {datetime.date.today()}", ln=True, align='C')
    pdf.ln(10)
    
    # Section-wise Profit Table
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, txt="Section Name", border=1)
    pdf.cell(90, 10, txt="Profit Level (1-200)", border=1, ln=True)
    
    pdf.set_font("Arial", size=12)
    for sec, val in sections_data.items():
        pdf.cell(100, 10, txt=sec, border=1)
        pdf.cell(90, 10, txt=str(val), border=1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"OVERALL PERFORMANCE SCORE: {overall_profit} / 200", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 3. UI LAYOUT ---
st.title("Smart Resource Allocation & Optimization")

# Institutional Levels Data
st.subheader("🏢 Section-Wise Profit Levels (Scale 1-200)")
col_p, col_s, col_c = st.columns(3)
with col_p: p_level = st.slider("Primary Profit", 1, 200, 85)
with col_s: s_level = st.slider("Secondary Profit", 1, 200, 110)
with col_c: c_level = st.slider("College Profit", 1, 200, 150)

overall_score = int((p_level + s_level + c_level) / 3)
st.metric("Total Institutional Profit Level", f"{overall_score}/200") [cite: 2025-12-29]

# Teacher Calculator
st.markdown("---")
st.subheader("👨‍🏫 Dynamic Teacher Load Calculator")
t_col1, t_col2, t_col3 = st.columns(3)
with t_col1: unit = st.selectbox("Select Unit", ["Daily", "Weekly", "Monthly"])
with t_col2: val = st.number_input(f"Enter {unit} Periods", value=3)
with t_col3: 
    m_p = get_monthly_periods(val, unit)
    advice, _ = get_status(m_p)
    st.write(f"Monthly Periods: **{m_p}**")
    st.info(advice)

# PDF Export Section
st.markdown("---")
if st.button("Prepare Final PDF Report"):
    sec_dict = {"Primary": p_level, "Secondary": s_level, "College": c_level}
    pdf_bytes = generate_institutional_report("My Institution", sec_dict, overall_score)
    
    st.download_button(
        label="📥 Download Professional Report",
        data=pdf_bytes,
        file_name="School_Optimization_Report.pdf",
        mime="application/pdf"
    )
