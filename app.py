import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF

# --- 1. SECURE LICENSE SYSTEM ---
# In a real app, this would be in a hidden secrets file
VALID_KEY = "PRO-MAX-200" 

def check_auth(user_key):
    return user_key == VALID_KEY

# --- 2. OPTIMIZATION LOGICS ---
def get_monthly_periods(value, unit):
    if unit == "Daily": return value * 26
    if unit == "Weekly": return value * 4
    return value

def get_teacher_status(m_periods):
    if m_periods < 40: return "🛑 Critical: Under-utilized (Resource Loss)"
    if m_periods > 120: return "🚨 Overload: High Teacher Burnout Risk"
    return "✅ Efficient: Perfect Resource Utilization"

def get_class_advice(students, max_cap):
    if students < 15: return "⚠️ Low Enrollment: Action Required (Merge Class)"
    elif students > max_cap: return f"🚨 Over-loaded: Capacity Exceeded (Split Section)"
    elif students >= (max_cap - 5): return "✅ Optimized: Near Full Capacity"
    return "✅ Stable"

# --- 3. PDF REPORT LOGIC ---
def generate_pdf_report(school_name, p_lvl, s_lvl, c_lvl, overall):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="School Resource Optimization Audit Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Institution Name: {school_name}", ln=True)
    pdf.cell(200, 10, txt=f"Audit Date: {datetime.date.today()}", ln=True)
    pdf.ln(10)
    
    # Section Table
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "Academic Department", 1)
    pdf.cell(90, 10, "Profit Level (1-200)", 1, ln=True)
    
    pdf.set_font("Arial", size=12)
    sections = {"Primary Department": p_lvl, "Secondary Department": s_lvl, "College Department": c_lvl}
    for sec, val in sections.items():
        pdf.cell(100, 10, sec, 1)
        pdf.cell(90, 10, str(val), 1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"INSTITUTIONAL EFFICIENCY SCORE: {overall} / 200", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 4. STREAMLIT UI ---
st.set_page_config(page_title="Institutional Optimizer Pro", layout="wide")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# LOGIN SCREEN (SECURE)
if not st.session_state.authenticated:
    st.title("🔐 Secure System Activation")
    st.write("Please enter your institutional credentials to access the dashboard.")
    
    inst_name = st.text_input("Institution Name", placeholder="e.g. City Excellence School")
    # type="password" hides the characters while typing
    input_key = st.text_input("License Key", type="password", placeholder="Enter your secret key here")
    
    if st.button("Activate Dashboard"):
        if check_auth(input_key):
            st.session_state.authenticated = True
            st.session_state.school_name = inst_name
            st.success("Access Granted!")
            st.rerun()
        else:
            st.error("Invalid License Key. Access Denied.")

# MAIN PROTECTED DASHBOARD
else:
    st.sidebar.title("Navigation")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

    st.title(f"🏫 {st.session_state.school_name} | Profit Optimization")
    
    # PROFIT LEVELS (1-200)
    st.markdown("---")
    st.subheader("📈 Sectional Performance (Profit Scale 1-200)")
    c1, c2, c3 = st.columns(3)
    with c1: p_val = st.number_input("Primary Profit", 1, 200, 85)
    with c2: s_val = st.number_input("Secondary Profit", 1, 200, 110)
    with c3: c_val = st.number_input("College Profit", 1, 200, 150)
    
    total_avg = int((p_val + s_val + c_val) / 3)
    st.markdown(f"### Overall Institutional Profit Level: **{total_avg} / 200**")
    st.progress(total_avg / 200)

    # CLASSROOM ADVISOR
    st.markdown("---")
    st.subheader("🏫 Smart Classroom Merge & Split Advisor")
    
    # Professional Data Table
    raw_data = [
        {"Class": "Grade 6", "Students": 12, "Room Capacity": 40},
        {"Class": "Grade 9", "Students": 55, "Room Capacity": 50}
    ]
    class_df = pd.DataFrame(raw_data)
    
    st.write("Edit the table below to analyze classroom efficiency:")
    edited_df = st.data_editor(class_df, num_rows="dynamic", use_container_width=True)
    
    if not edited_df.empty:
        edited_df['System Advice'] = edited_df.apply(
            lambda x: get_class_advice(x['Students'], x['Room Capacity']), axis=1
        )
        st.dataframe(edited_df, use_container_width=True)

    # TEACHER WORKLOAD
    st.markdown("---")
    st.subheader("👨‍🏫 Teacher Load & Efficiency Analyzer")
    t1, t2, t3 = st.columns(3)
    with t1: unit = st.selectbox("Select Calculation Unit", ["Daily", "Weekly", "Monthly"])
    with t2: period_input = st.number_input(f"Enter {unit} Periods", min_value=1, value=5)
    with t3:
        m_total = get_monthly_periods(period_input, unit)
        advice = get_teacher_status(m_total)
        st.write(f"Total Monthly Periods: **{m_total}**")
        st.info(advice)

    # REPORTING
    st.markdown("---")
    if st.button("Finalize and Generate PDF Audit Report"):
        report = generate_pdf_report(st.session_state.school_name, p_val, s_val, c_val, total_avg)
        st.download_button(
            label="📥 Download Audit Report",
            data=report,
            file_name=f"Optimization_Audit_{st.session_state.school_name}.pdf",
            mime="application/pdf"
        )
