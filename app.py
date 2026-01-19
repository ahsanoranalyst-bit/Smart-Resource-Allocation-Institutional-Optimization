import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF

# --- 1. SECURE LICENSE SYSTEM ---
VALID_KEY = "PRO-MAX-200" 
def check_auth(user_key):
    return user_key == VALID_KEY

# --- 2. LOGIC FUNCTIONS ---
def get_class_advice(students, capacity):
    if students < 15: return "⚠️ Merge Class"
    if students > capacity: return "🚨 Split Section"
    return "✅ Optimized"

# --- 3. PDF REPORT GENERATION ---
def generate_audit_report(school, p_score, s_score, c_score, final_score, total_exp):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Detailed Institutional Audit Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Institution: {school}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {datetime.date.today()}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "Academic Section", 1)
    pdf.cell(90, 10, "Profit Level (1-200)", 1, ln=True)
    
    sections = [("Primary", p_score), ("Secondary", s_score), ("College", c_score)]
    pdf.set_font("Arial", size=12)
    for name, score in sections:
        pdf.cell(100, 10, name, 1)
        pdf.cell(90, 10, str(score), 1, ln=True)
        
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"FINAL STRATEGIC PROFIT LEVEL: {final_score} / 200", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 4. STREAMLIT UI ---
st.set_page_config(page_title="Smart Institutional Optimizer", layout="wide")

if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Secure System Activation")
    inst_name = st.text_input("Institution Name")
    key = st.text_input("License Key", type="password")
    if st.button("Activate Dashboard"):
        if check_auth(key):
            st.session_state.auth = True
            st.session_state.school = inst_name
            st.rerun()
        else: st.error("Access Denied.")

else:
    st.title(f"🏫 {st.session_state.school} | Result-Based Manager")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["👶 Primary", "🏫 Secondary", "🎓 College", "🏢 Gen Expenses", "📋 Final Audit"])

    def handle_section(section_name, key_prefix):
        st.subheader(f"{section_name} Class-wise Entry")
        st.write(f"Use the '+' at the bottom of the table to add more classes.")
        
        # Default data for the table
        default_data = [{"Class": "Class 1", "Students": 20, "Fee Per Student": 3000}]
        df = pd.DataFrame(default_data)
        
        # Data editor acts as the dynamic table with plus sign
        edited_df = st.data_editor(df, num_rows="dynamic", key=f"editor_{key_prefix}", use_container_width=True)
        
        total_revenue = 0
        total_students = 0
        if not edited_df.empty:
            edited_df['Total Revenue'] = edited_df['Students'] * edited_df['Fee Per Student']
            total_revenue = edited_df['Total Revenue'].sum()
            total_students = edited_df['Students'].sum()
            
        st.write(f"**Total {section_name} Students:** {total_students}")
        st.write(f"**Total {section_name} Revenue:** {total_revenue} PKR")
        
        salaries = st.number_input(f"Total Staff Salaries ({section_name})", value=50000, key=f"sal_{key_prefix}")
        net_sec = total_revenue - salaries
        
        # Advice Logic
        if not edited_df.empty:
            st.write("#### Classroom Advice:")
            advice_df = edited_df.copy()
            # Assuming a standard capacity of 40 for advice, can be made dynamic later
            advice_df['Advice'] = advice_df.apply(lambda x: get_class_advice(x['Students'], 40), axis=1)
            st.table(advice_df[['Class', 'Students', 'Advice']])
            
        return total_revenue, net_sec

    with tab1:
        p_rev, p_net = handle_section("Primary", "pri")

    with tab2:
        s_rev, s_net = handle_section("Secondary", "sec")

    with tab3:
        c_rev, c_net = handle_section("College", "col")

    with tab4:
        st.subheader("General Institutional Expenses")
        c1, c2 = st.columns(2)
        with c1:
            rent = st.number_input("Building Rent", value=30000)
            util = st.number_input("Electricity & Bills", value=15000)
        with c2:
            labor = st.number_input("Labor & Non-Teaching Staff", value=20000)
            misc = st.number_input("Other Expenses", value=5000)
        
        total_gen_exp = rent + util + labor + misc
        st.error(f"Total Operational Cost: {total_gen_exp} PKR")

    with tab5:
        st.subheader("Final Performance Audit")
        
        total_school_rev = p_rev + s_rev + c_rev
        total_school_net = p_net + s_net + c_net - total_gen_exp
        
        if total_school_rev > 0:
            # Scaling margin to 1-200 [cite: 2025-12-29]
            margin = total_school_net / total_school_rev
            final_score = max(1, min(200, int(margin * 400)))
        else:
            final_score = 1
            
        # Individual scores for PDF
        p_score = max(1, min(200, int((p_net/p_rev)*400))) if p_rev > 0 else 1
        s_score = max(1, min(200, int((s_net/s_rev)*400))) if s_rev > 0 else 1
        c_score = max(1, min(200, int((c_net/c_rev)*400))) if c_rev > 0 else 1

        st.header(f"Final Profit Level: {final_score} / 200")
        st.progress(final_score / 200)
        
        if st.button("Generate & Download Final Audit PDF"):
            pdf_bytes = generate_audit_report(st.session_state.school, p_score, s_score, c_score, final_score, total_gen_exp)
            st.download_button("📥 Download PDF Report", data=pdf_bytes, file_name="School_Full_Audit.pdf")

    if st.sidebar.button("Log Out"):
        st.session_state.auth = False
        st.rerun()
