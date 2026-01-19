import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF

# --- 1. SECURE LICENSE ---
VALID_KEY = "PRO-MAX-200" 
def check_auth(key): return key == VALID_KEY

# --- 2. LOGIC FUNCTIONS ---
def get_class_advice(students, capacity):
    if students < 15: return "⚠️ Critical: Low Strength (Merge Class)"
    if students > capacity: return "🚨 Alert: Over-loaded (Split Section)"
    return "✅ Optimized: Efficient Capacity"

def get_teacher_efficiency(val, unit):
    # Convert to monthly periods
    if unit == "Daily": m_p = val * 26
    elif unit == "Weekly": m_p = val * 4
    else: m_p = val
    
    if m_p < 40: return m_p, "🛑 Under-utilized", "Red"
    if m_p > 120: return m_p, "🚨 Over-loaded", "Red"
    return m_p, "✅ Efficient", "Green"

# --- 3. PDF GENERATION ---
def generate_master_report(school, p_score, s_score, c_score, final_score, total_exp):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(200, 15, txt="Strategic Institutional Audit", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Institution: {school} | Date: {datetime.date.today()}", ln=True, align='C')
    pdf.ln(10)
    
    # Financial Summary Table
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "Section/Metric", 1)
    pdf.cell(90, 10, "Status/Level", 1, ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, "Primary Section Profit Level", 1)
    pdf.cell(90, 10, f"{p_score}/200", 1, ln=True)
    pdf.cell(100, 10, "Secondary Section Profit Level", 1)
    pdf.cell(90, 10, f"{s_score}/200", 1, ln=True)
    pdf.cell(100, 10, "Total Monthly Operational Costs", 1)
    pdf.cell(90, 10, f"{total_exp} PKR", 1, ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"FINAL SCORE: {final_score} / 200", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- 4. UI SETUP ---
st.set_page_config(page_title="Strategic School Optimizer", layout="wide")

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 System Activation")
    inst_name = st.text_input("Institution Name", placeholder="Enter School Name")
    key = st.text_input("License Key", type="password", placeholder="Enter Secret Key")
    if st.button("Activate Dashboard"):
        if check_auth(key):
            st.session_state.auth = True
            st.session_state.school = inst_name
            st.rerun()
        else: st.error("Invalid Key. Access Denied.")

else:
    st.sidebar.title(f"🏫 {st.session_state.school}")
    if st.sidebar.button("System Logout"):
        st.session_state.auth = False
        st.rerun()

    # --- TABS FOR COMPLETE MANAGEMENT ---
    tabs = st.tabs(["👶 Primary", "🏫 Secondary", "🎓 College", "👨‍🏫 Staff Load", "🏗️ Admin Expenses", "📊 Final Audit"])

    def process_section(name, key):
        st.subheader(f"{name} Section - Revenue & Class Management")
        with st.expander(f"Add/Edit {name} Classes", expanded=True):
            df = pd.DataFrame([{"Class": "Entry 1", "Students": 25, "Fee": 5000, "Room Capacity": 40}])
            edited = st.data_editor(df, num_rows="dynamic", key=f"edit_{key}", use_container_width=True)
            
            total_rev, total_std = 0, 0
            if not edited.empty:
                edited['Class Revenue'] = edited['Students'] * edited['Fee']
                total_rev = edited['Class Revenue'].sum()
                total_std = edited['Students'].sum()
                edited['Advice'] = edited.apply(lambda x: get_class_advice(x['Students'], x['Room Capacity']), axis=1)
                st.write("#### 💡 Capacity Advisor:")
                st.table(edited[['Class', 'Students', 'Room Capacity', 'Advice']])

        salaries = st.number_input(f"Total Staff Salaries ({name})", value=100000, key=f"sal_{key}")
        net = total_rev - salaries
        return total_rev, net

    # Primary, Secondary, College Logic
    with tabs[0]: p_rev, p_net = process_section("Primary", "pri")
    with tabs[1]: s_rev, s_net = process_section("Secondary", "sec")
    with tabs[2]: c_rev, c_net = process_section("College", "col")

    # Staff Loading Analysis
    with tabs[3]:
        st.subheader("Teacher Efficiency & Load Tracker")
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1: unit = st.selectbox("Select Unit", ["Daily", "Weekly", "Monthly"])
        with t_col2: val = st.number_input(f"No. of Periods", value=6)
        with t_col3:
            m_load, status, color = get_teacher_efficiency(val, unit)
            st.metric("Monthly Period Load", m_load)
            if color == "Red": st.error(status)
            else: st.success(status)

    # General Expenses
    with tabs[4]:
        st.subheader("General Operational Expenses")
        e_c1, e_c2 = st.columns(2)
        with e_c1:
            rent = st.number_input("Building Rent", value=40000)
            bills = st.number_input("Electricity & Utilities", value=20000)
        with e_c2:
            labor = st.number_input("Labor & Security", value=25000)
            misc = st.number_input("Other (Admin)", value=5000)
        total_gen_exp = rent + bills + labor + misc
        st.warning(f"Total Operational Cost: {total_gen_exp} PKR")

    # Final Audit & PDF
    with tabs[5]:
        st.subheader("Institutional Efficiency Audit")
        total_rev = p_rev + s_rev + c_rev
        total_net = p_net + s_net + c_net - total_gen_exp
        
        # Scoring logic (1-200) based on margins [cite: 2025-12-29]
        def score_me(net, rev): return max(1, min(200, int((net/rev)*400))) if rev > 0 else 1
        
        p_score = score_me(p_net, p_rev)
        s_score = score_me(s_net, s_rev)
        c_score = score_me(c_net, c_rev)
        final_score = score_me(total_net, total_rev)

        st.header(f"Total Strategic Profit Level: {final_score} / 200")
        st.progress(final_score / 200)

        if st.button("Finalize and Download Audit PDF"):
            pdf_bytes = generate_master_report(st.session_state.school, p_score, s_score, c_score, final_score, total_gen_exp)
            st.download_button("📥 Download Official Report", data=pdf_bytes, file_name="Audit_Report.pdf")
