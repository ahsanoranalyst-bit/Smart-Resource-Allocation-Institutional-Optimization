import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF

# --- 1. LICENSE SYSTEM ---
MASTER_LICENSE_KEY = "PRO-MAX-200"

def validate_license(key):
    return key == MASTER_LICENSE_KEY

# --- 2. OPTIMIZATION LOGIC ---
def get_monthly_periods(value, unit):
    if unit == "Daily": return value * 26
    if unit == "Weekly": return value * 4
    return value

def get_teacher_status(m_periods):
    if m_periods < 40: return "🛑 Critical: Under-utilized (Loss)"
    if m_periods > 120: return "🚨 Overload: Staff Burnout Risk"
    return "✅ Efficient: Perfect Resource Use"

def get_class_advice(students, max_cap):
    if students < 15: return "⚠️ Low Enrollment: Merge this Class"
    elif students > max_cap: return f"🚨 Over-crowded: Split into New Section"
    elif students >= (max_cap - 5): return "✅ Optimized: Near Full Capacity"
    return "✅ Stable"

# --- 3. PDF REPORT GENERATION ---
def generate_report(school_name, p_lvl, s_lvl, c_lvl, overall):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Institutional Resource Optimization Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Institution: {school_name}", ln=True)
    pdf.cell(200, 10, txt=f"Analysis Date: {datetime.date.today()}", ln=True)
    pdf.ln(10)
    
    # Section Profit Table
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "Academic Section", 1)
    pdf.cell(90, 10, "Profit Level (1-200)", 1, ln=True)
    pdf.set_font("Arial", size=12)
    sections = {"Primary Section": p_lvl, "Secondary Section": s_lvl, "College Section": c_lvl}
    for sec, val in sections.items():
        pdf.cell(100, 10, sec, 1)
        pdf.cell(90, 10, str(val), 1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"FINAL STRATEGIC PROFIT SCORE: {overall} / 200", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 4. STREAMLIT INTERFACE ---
st.set_page_config(page_title="Smart School Optimizer Pro", layout="wide")

if 'auth' not in st.session_state:
    st.session_state.auth = False

# LOGIN SCREEN
if not st.session_state.auth:
    st.title("🔐 System Activation")
    st.subheader("Institutional Optimization & Profit Management System")
    school_input = st.text_input("Institution Name")
    key_input = st.text_input("Enter License Key (PRO-MAX-200)", type="password")
    if st.button("Activate Dashboard"):
        if validate_license(key_input):
            st.session_state.auth = True
            st.session_state.school = school_input
            st.rerun()
        else:
            st.error("Invalid License Key. Access Denied.")

# MAIN DASHBOARD
else:
    st.title(f"🏫 {st.session_state.school} | Strategic Dashboard")
    
    # 1. SECTIONAL PROFIT LEVELS (1-200)
    st.markdown("---")
    st.subheader("📊 Section-wise Profit Performance")
    c1, c2, c3 = st.columns(3)
    with c1: p_val = st.number_input("Primary Profit Level", 1, 200, 85)
    with c2: s_val = st.number_input("Secondary Profit Level", 1, 200, 110)
    with c3: c_val = st.number_input("College Profit Level", 1, 200, 150)
    
    overall_score = int((p_val + s_val + c_val) / 3)
    st.markdown(f"### Total Institutional Profit Level: **{overall_score} / 200**")
    st.progress(overall_score/200)

    # 2. CLASSROOM OPTIMIZATION (ADVISOR)
    st.markdown("---")
    st.subheader("🏫 Classroom Capacity & Merge Advisor")
    st.write("Input current student count and room capacity to see system recommendations.")
    
    class_df = pd.DataFrame([
        {"Class Name": "Grade 5-A", "Students": 12, "Max Capacity": 40},
        {"Class Name": "Grade 10-B", "Students": 45, "Max Capacity": 40}
    ])
    
    # Editable Table
    edited_df = st.data_editor(class_df, num_rows="dynamic", use_container_width=True)
    
    if not edited_df.empty:
        edited_df['System Advice'] = edited_df.apply(
            lambda x: get_class_advice(x['Students'], x['Max Capacity']), axis=1
        )
        st.write("### 📢 Live Optimization Advice:")
        st.table(edited_df[['Class Name', 'Students', 'Max Capacity', 'System Advice']])

    # 3. TEACHER WORKLOAD ANALYZER (FLEXIBLE)
    st.markdown("---")
    st.subheader("👨‍🏫 Teacher Efficiency & Workload Analyzer")
    t1, t2, t3, t4 = st.columns(4)
    with t1: teacher_name = st.text_input("Staff Name", "Teacher 1")
    with t2: unit = st.selectbox("Input Unit", ["Daily", "Weekly", "Monthly"])
    with t3: val = st.number_input(f"Periods ({unit})", value=4)
    with t4:
        m_periods = get_monthly_periods(val, unit)
        t_advice = get_teacher_status(m_periods)
        st.write(f"Calculated Monthly Load: **{m_periods} Periods**")
        st.info(t_advice)

    # 4. REPORT EXPORT
    st.markdown("---")
    if st.button("Generate Professional Audit Report"):
        report_bytes = generate_report(st.session_state.school, p_val, s_val, c_val, overall_score)
        st.download_button(
            label="📥 Download PDF Optimization Report",
            data=report_bytes,
            file_name=f"{st.session_state.school}_Audit_Report.pdf",
            mime="application/pdf"
        )

    if st.sidebar.button("Logout System"):
        st.session_state.auth = False
        st.rerun()
