import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF

# --- 1. SECURE LICENSE SYSTEM ---
VALID_KEY = "PRO-MAX-200" 
def check_auth(user_key):
    return user_key == VALID_KEY

# --- 2. ADVANCED PROFIT LOGIC ---
def calculate_section_revenue(students, fee):
    return students * fee

def get_class_advice(students, capacity):
    if students < 15: return "⚠️ Low Enrollment: Merge Class"
    if students > capacity: return "🚨 Over-loaded: Split Section"
    return "✅ Optimized"

# --- 3. PDF REPORT GENERATION ---
def generate_audit_report(school, p_score, s_score, c_score, final_score, expenses_total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Institutional Audit & Optimization Report", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Institution: {school}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {datetime.date.today()}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "Component", 1)
    pdf.cell(90, 10, "Value / Score", 1, ln=True)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, "Primary Profit Level", 1)
    pdf.cell(90, 10, str(p_score), 1, ln=True)
    pdf.cell(100, 10, "Secondary Profit Level", 1)
    pdf.cell(90, 10, str(s_score), 1, ln=True)
    pdf.cell(100, 10, "College Profit Level", 1)
    pdf.cell(90, 10, str(c_score), 1, ln=True)
    pdf.cell(100, 10, "Total Monthly Operational Costs", 1)
    pdf.cell(90, 10, f"{expenses_total} PKR", 1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"FINAL STRATEGIC PROFIT LEVEL: {final_score} / 200", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 4. APP INTERFACE ---
st.set_page_config(page_title="Smart Institutional Optimizer", layout="wide")

if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Secure Activation")
    inst_name = st.text_input("Institution Name")
    key = st.text_input("License Key", type="password")
    if st.button("Activate Dashboard"):
        if check_auth(key):
            st.session_state.auth = True
            st.session_state.school = inst_name
            st.rerun()
        else: st.error("Access Denied.")

else:
    st.title(f"🏫 {st.session_state.school} | Master Control Dashboard")
    
    # Tabs for Organization
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Income & Sections", "🏢 General Expenses", "🏫 Classroom Manager", "📋 Final Report"])

    with tab1:
        st.subheader("Section-wise Revenue & Teaching Costs")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("### Primary")
            p_s = st.number_input("Students (Pri)", value=100)
            p_f = st.number_input("Avg Fee (Pri)", value=4000)
            p_sal = st.number_input("Salaries (Pri)", value=150000)
            p_rev = calculate_section_revenue(p_s, p_f)
            p_net = p_rev - p_sal
            
        with col2:
            st.write("### Secondary")
            s_s = st.number_input("Students (Sec)", value=80)
            s_f = st.number_input("Avg Fee (Sec)", value=6000)
            s_sal = st.number_input("Salaries (Sec)", value=200000)
            s_rev = calculate_section_revenue(s_s, s_f)
            s_net = s_rev - s_sal

        with col3:
            st.write("### College")
            c_active = st.checkbox("Include College", value=False)
            if c_active:
                c_s = st.number_input("Students (Col)", value=40)
                c_f = st.number_input("Avg Fee (Col)", value=10000)
                c_sal = st.number_input("Salaries (Col)", value=150000)
                c_rev = calculate_section_revenue(c_s, c_f)
                c_net = c_rev - c_sal
            else:
                c_rev, c_net = 0, 0

    with tab2:
        st.subheader("General Operational Expenses")
        st.write("Enter costs that apply to the whole building/institution.")
        exp_col1, exp_col2 = st.columns(2)
        with exp_col1:
            rent = st.number_input("Building Rent / Maintenance", value=50000)
            electricity = st.number_input("Electricity & Utilities", value=30000)
        with exp_col2:
            labor = st.number_input("Non-Teaching Staff / Labor", value=40000)
            misc = st.number_input("Misc / Admin Costs", value=10000)
        
        total_gen_expenses = rent + electricity + labor + misc
        st.warning(f"Total General Expenses: {total_gen_expenses} PKR")

    with tab3:
        st.subheader("Classroom Capacity Advisor")
        class_data = pd.DataFrame([{"Class": "6th-A", "Students": 12, "Capacity": 40}])
        edited_class = st.data_editor(class_data, num_rows="dynamic", key="class_edit", use_container_width=True)
        if not edited_class.empty:
            edited_class['Advice'] = edited_class.apply(lambda x: get_class_advice(x['Students'], x['Capacity']), axis=1)
            st.dataframe(edited_class, use_container_width=True)

    with tab4:
        st.subheader("Final Strategic Analysis")
        
        # Calculating Final Profit Score (1-200)
        total_net_profit = p_net + s_net + c_net - total_gen_expenses
        total_revenue = p_rev + s_rev + c_rev
        
        if total_revenue > 0:
            margin = total_net_profit / total_revenue
            # Scaling logic to fit 1-200 [cite: 2025-12-29]
            final_score = max(1, min(200, int(margin * 400))) 
        else:
            final_score = 1

        # Sectional Scores for Report
        p_score = max(1, min(200, int((p_net/p_rev)*400))) if p_rev > 0 else 1
        s_score = max(1, min(200, int((s_net/s_rev)*400))) if s_rev > 0 else 1
        c_score = max(1, min(200, int((c_net/c_rev)*400))) if c_rev > 0 else 1

        st.header(f"Final Profit Level: {final_score} / 200")
        st.progress(final_score / 200)
        
        if st.button("Generate & Download PDF Audit Report"):
            report_bytes = generate_audit_report(st.session_state.school, p_score, s_score, c_score, final_score, total_gen_expenses)
            st.download_button(label="📥 Download Audit Report", data=report_bytes, file_name="Institutional_Audit.pdf", mime="application/pdf")

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
