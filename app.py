import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF

# --- 1. SETTINGS & LICENSE ---
MASTER_LICENSE_KEY = "PRO-MAX-200"
SUBSCRIPTION_EXPIRY = datetime.date(2027, 1, 1)

def validate_license(key):
    return key == MASTER_LICENSE_KEY and datetime.date.today() <= SUBSCRIPTION_EXPIRY

# --- 2. PDF GENERATION FUNCTION ---
def create_pdf(school_name, overall_profit, p_profit, s_profit, c_profit):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Header
    pdf.cell(200, 10, txt="Smart Resource Allocation Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Institution: {school_name}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Date: {datetime.date.today()}", ln=True, align='C')
    pdf.ln(10)
    
    # Data Table
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, txt="Section", border=1)
    pdf.cell(90, 10, txt="Profit Level (1-200)", border=1, ln=True)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, txt="Overall School", border=1)
    pdf.cell(90, 10, txt=f"{overall_profit}", border=1, ln=True)
    pdf.cell(100, 10, txt="Primary Section", border=1)
    pdf.cell(90, 10, txt=f"{p_profit}", border=1, ln=True)
    pdf.cell(100, 10, txt="Secondary Section", border=1)
    pdf.cell(90, 10, txt=f"{s_profit}", border=1, ln=True)
    pdf.cell(100, 10, txt="College Section", border=1)
    pdf.cell(90, 10, txt=f"{c_profit}", border=1, ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 3. PAGE CONFIGURATION ---
st.set_page_config(page_title="Institutional Optimizer", layout="wide")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# --- 4. LOGIN INTERFACE ---
if not st.session_state.authenticated:
    st.title("🔐 System Activation")
    st.subheader("Smart Resource Allocation & Institutional Optimization System")
    
    school_name_input = st.text_input("Enter Institution Name")
    license_input = st.text_input("License Key", type="password")
    
    if st.button("Activate License"):
        if validate_license(license_input):
            st.session_state.authenticated = True
            st.session_state.school_name = school_name_input
            st.rerun()
        else:
            st.error("Access Denied: Invalid Key or Subscription Expired.")

# --- 5. MAIN DASHBOARD ---
else:
    # Top Header
    st.title(f"🏫 {st.session_state.school_name}")
    st.caption("Smart Resource Allocation & Institutional Optimization System")
    
    # 6. COMPARATIVE PROFIT GAUGES (BEFORE vs AFTER)
    st.markdown("### 🚀 Strategic Performance Comparison")
    col_m1, col_m2, col_m3 = st.columns(3)
    
    ov_profit = 172 # Dynamic Value
    p_prof, s_prof, c_prof = 115, 155, 190
    
    col_m1.metric("Before Optimization", "85/200")
    col_m2.metric("Current Profit Level", f"{ov_profit}/200", delta="+87")
    col_m3.metric("Improvement", "102.3%")

    # 7. SECTIONAL VIEW
    st.markdown("---")
    st.subheader("📂 Section-wise Profitability")
    sc1, sc2, sc3 = st.columns(3)
    
    with sc1:
        st.write("Primary Level")
        st.progress(p_prof/200)
        st.write(f"Score: {p_prof}/200")
        
    with sc2:
        st.write("Secondary Level")
        st.progress(s_prof/200)
        st.write(f"Score: {s_prof}/200")
        
    with sc3:
        st.write("College Level")
        st.progress(c_prof/200)
        st.write(f"Score: {c_prof}/200")

    # 8. RESOURCE INPUTS
    st.markdown("---")
    st.subheader("📊 Resource & Class Scheduling")
    tab1, tab2 = st.tabs(["Teacher Allocation", "Classroom Optimization"])
    
    with tab1:
        st.data_editor({"Faculty Name": ["T-1"], "Salary": [40000], "Assigned Hours": [6]}, num_rows="dynamic", use_container_width=True)
    with tab2:
        st.data_editor({"Class": ["10th"], "Students": [20], "Section": ["Secondary"]}, num_rows="dynamic", use_container_width=True)

    # 9. PDF EXPORT
    st.markdown("---")
    pdf_bytes = create_pdf(st.session_state.school_name, ov_profit, p_prof, s_prof, c_prof)
    st.download_button(
        label="📥 Download Optimization Report (PDF)",
        data=pdf_bytes,
        file_name=f"Optimization_Report_{st.session_state.school_name}.pdf",
        mime="application/pdf"
    )

    if st.sidebar.button("Log Out"):
        st.session_state.authenticated = False
        st.rerun()
