import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF

# --- 1. SECURE LICENSE SYSTEM ---
VALID_KEY = "PRO-MAX-200" 
def check_auth(key): return key == VALID_KEY

# --- 2. STAFF CAPACITY & EFFICIENCY LOGIC ---
def analyze_staff_load(row, unit):
    assigned = row['Assigned Periods']
    capacity = row['Teacher Capacity']
    salary = row['Salary']
    
    # Monthly Calculation
    if unit == "Daily": m_p = assigned * 26
    elif unit == "Weekly": m_p = assigned * 4
    else: m_p = assigned
    
    cost_per_p = salary / m_p if m_p > 0 else 0
    diff = assigned - capacity
    
    if assigned < capacity:
        status = f"🛑 Under-filled (Gap: {abs(diff)} p)"
        color = "red"
        advice = "Increase load to optimize salary."
    elif assigned == capacity:
        status = "✅ Efficient (Ideal Fill)"
        color = "green"
        advice = "Perfect Resource Usage."
    else:
        status = f"🚨 Overloaded (Extra: {diff} p)"
        color = "orange"
        advice = "Quality Risk! Reduce burden."
        
    return pd.Series([m_p, round(cost_per_p, 2), status, advice])

# --- 3. CLASS & PROFIT LOGIC ---
def get_class_advice(students, cap):
    if students < 15: return "⚠️ Merge Class"
    if students > cap: return "🚨 Split Section"
    return "✅ Optimized"

# --- 4. PDF GENERATION ---
def generate_pdf(school, final_score, total_exp):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Institutional Resource Audit", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Institution: {school} | Score: {final_score}/200", ln=True)
    pdf.cell(200, 10, txt=f"Total Operational Expenses: {total_exp} PKR", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 5. UI SETUP ---
st.set_page_config(page_title="Institutional Master Optimizer", layout="wide")

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Secure System Activation")
    key = st.text_input("License Key", type="password")
    if st.button("Activate Dashboard"):
        if check_auth(key):
            st.session_state.auth = True
            st.session_state.school = "My Institution"
            st.rerun()
        else: st.error("Access Denied.")

else:
    st.title(f"🏫 {st.session_state.school} | Master Dashboard")
    tabs = st.tabs(["👨‍🏫 Staff Capacity Audit", "👶 Primary", "🏫 Secondary", "🎓 College", "🏗️ Admin Expenses", "📊 Final Audit"])

    # --- STAFF CAPACITY TAB ---
    with tabs[0]:
        st.subheader("Teacher Workload & ROI Gauge")
        unit = st.radio("Period Unit:", ["Daily", "Weekly", "Monthly"], horizontal=True)
        staff_df = pd.DataFrame([{"Teacher Name": "Teacher A", "Salary": 40000, "Teacher Capacity": 8, "Assigned Periods": 6}])
        edited_staff = st.data_editor(staff_df, num_rows="dynamic", key="staff_gauge", use_container_width=True)
        
        if not edited_staff.empty:
            results = edited_staff.apply(lambda row: analyze_staff_load(row, unit), axis=1)
            edited_staff[['Monthly Periods', 'Cost/Period', 'Loading Status', 'Strategic Advice']] = results
            st.dataframe(edited_staff, use_container_width=True)

    # --- SECTION LOGIC (REUSABLE) ---
    def handle_sec(name, key):
        st.subheader(f"{name} Class-wise Data")
        df = pd.DataFrame([{"Class": "Class 1", "Students": 20, "Fee": 4000, "Room Cap": 40}])
        edited = st.data_editor(df, num_rows="dynamic", key=f"edit_{key}", use_container_width=True)
        total_rev = 0
        if not edited.empty:
            edited['Revenue'] = edited['Students'] * edited['Fee']
            total_rev = edited['Revenue'].sum()
            edited['Advice'] = edited.apply(lambda x: get_class_advice(x['Students'], x['Room Cap']), axis=1)
            st.table(edited[['Class', 'Students', 'Advice']])
        sal = st.number_input(f"Total Staff Salaries ({name})", value=50000, key=f"sal_{key}")
        return total_rev, total_rev - sal

    with tabs[1]: p_rev, p_net = handle_sec("Primary", "pri")
    with tabs[2]: s_rev, s_net = handle_sec("Secondary", "sec")
    with tabs[3]: c_rev, c_net = handle_sec("College", "col")

    # --- ADMIN EXPENSES ---
    with tabs[4]:
        st.subheader("General Operational Expenses")
        rent = st.number_input("Building Rent", value=40000)
        util = st.number_input("Electricity & Bills", value=20000)
        labor = st.number_input("Labor & Security", value=20000)
        total_gen_exp = rent + util + labor
        st.warning(f"Total Fixed Expenses: {total_gen_exp} PKR")

    # --- FINAL AUDIT ---
    with tabs[5]:
        st.subheader("Final Strategic Audit")
        total_rev = p_rev + s_rev + c_rev
        total_net = p_net + s_net + c_net - total_gen_exp
        
        # Profit Level Logic (1-200) [cite: 2025-12-29]
        score = max(1, min(200, int((total_net/total_rev)*400))) if total_rev > 0 else 1
        
        st.header(f"Institutional Profit Level: {score} / 200")
        st.progress(score / 200)
        
        if st.button("Generate Audit PDF"):
            pdf_bytes = generate_pdf(st.session_state.school, score, total_gen_exp)
            st.download_button("📥 Download PDF Report", data=pdf_bytes, file_name="Full_Audit.pdf")

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
