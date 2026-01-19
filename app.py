import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF

# --- 1. SECURE LICENSE SYSTEM ---
VALID_KEY = "PRO-MAX-200" 
def check_auth(key):
    return key == VALID_KEY

# --- 2. ADVANCED LOGIC FUNCTIONS ---
def analyze_staff_row(row):
    """Calculates efficiency and cost per teacher based on individual units."""
    assigned = row['Assigned Periods']
    capacity = row['Teacher Capacity']
    salary = row['Salary']
    unit = row['Reporting Unit']
    
    # Normalize to Monthly Periods
    if unit == "Daily": m_p = assigned * 26
    elif unit == "Weekly": m_p = assigned * 4
    else: m_p = assigned # Monthly
    
    cost_per_p = salary / m_p if m_p > 0 else 0
    diff = assigned - capacity
    
    if assigned < capacity: 
        status = "🛑 Under-filled"
        advice = f"Increase load (Gap: {abs(diff)} p)"
    elif assigned == capacity: 
        status = "✅ Efficient"
        advice = "Ideal usage of resource."
    else: 
        status = "🚨 Overloaded"
        advice = f"Burnout risk (Extra: {diff} p)"
    
    return pd.Series([m_p, round(cost_per_p, 2), status, advice])

def get_class_advice(students, cap):
    """Provides classroom management advice based on strength."""
    if students < 15: return "⚠️ Critical: Merge Class"
    if students > cap: return "🚨 Alert: Split Section"
    return "✅ Optimized Strength"

# --- 3. UI CONFIGURATION ---
st.set_page_config(page_title="Institutional Master Optimizer", layout="wide")

if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'school_name' not in st.session_state:
    st.session_state.school_name = ""

# --- LOGIN SCREEN ---
if not st.session_state.auth:
    st.title("🔐 Strategic System Activation")
    st.markdown("Please enter your official details to access the dashboard.")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        school_input = st.text_input("Enter School / Institution Name", placeholder="e.g., Global Excellence School")
    with col_l2:
        key_input = st.text_input("Enter License Key", type="password", placeholder="Secret Access Key")
    
    if st.button("Activate Dashboard"):
        if check_auth(key_input) and school_input:
            st.session_state.auth = True
            st.session_state.school_name = school_input
            st.rerun()
        elif not school_input:
            st.error("Please provide the Institution Name.")
        else:
            st.error("Invalid License Key. Access Denied.")

# --- AUTHORIZED DASHBOARD ---
else:
    st.sidebar.title(f"🏫 {st.session_state.school_name}")
    st.sidebar.info(f"System Status: Active\nDate: {datetime.date.today()}")
    
    tabs = st.tabs(["👨‍🏫 Staff Audit", "👶 Sections Profit", "🏗️ Admin Expenses", "📊 Final Audit Gauge"])

    # --- TAB 1: STAFF AUDIT (WITH INDIVIDUAL UNITS) ---
    with tabs[0]:
        st.subheader("Teacher Capacity & ROI Audit")
        st.write("Analyze individual staff workload and cost-efficiency.")
        
        staff_data = pd.DataFrame([
            {"Teacher Name": "Teacher 1", "Salary": 45000, "Reporting Unit": "Daily", "Teacher Capacity": 8, "Assigned Periods": 6}
        ])
        
        # Column configuration for the dropdown unit selector
        col_config = {
            "Reporting Unit": st.column_config.SelectboxColumn(
                "Reporting Unit",
                options=["Daily", "Weekly", "Monthly"],
                required=True,
            )
        }
        
        edited_staff = st.data_editor(staff_data, num_rows="dynamic", key="staff_audit_table", column_config=col_config, use_container_width=True)
        
        if not edited_staff.empty:
            staff_res = edited_staff.apply(analyze_staff_row, axis=1)
            edited_staff[['Total Monthly', 'Cost/Period', 'Loading Status', 'Strategic Advice']] = staff_res
            st.dataframe(edited_staff, use_container_width=True)

    # --- TAB 2: SECTIONS PROFIT ---
    with tabs[1]:
        def handle_sec(name, key_prefix):
            st.subheader(f"📊 {name} Revenue & Class Management")
            class_df = pd.DataFrame([{"Class": "Grade 1", "Students": 30, "Fee": 5000, "Room Capacity": 40}])
            edited_cls = st.data_editor(class_df, num_rows="dynamic", key=f"cls_{key_prefix}", use_container_width=True)
            
            total_rev = 0
            if not edited_cls.empty:
                edited_cls['Revenue'] = edited_cls['Students'] * edited_cls['Fee']
                total_rev = edited_cls['Revenue'].sum()
                edited_cls['Advice'] = edited_cls.apply(lambda x: get_class_advice(x['Students'], x['Room Capacity']), axis=1)
                st.table(edited_cls[['Class', 'Students', 'Advice']])
            
            salaries = st.number_input(f"Total Staff Salaries for {name}", value=100000, key=f"sal_{key_prefix}")
            sec_profit = total_rev - salaries
            st.metric(f"{name} Gross Contribution", f"{sec_profit} PKR")
            return total_rev, sec_profit

        p_rev, p_net = handle_sec("Primary", "pri")
        st.divider()
        s_rev, s_net = handle_sec("Secondary", "sec")
        st.divider()
        c_rev, c_net = handle_sec("College", "col")

    # --- TAB 3: ADMIN & OTHER EXPENSES ---
    with tabs[2]:
        st.subheader("🏗️ General & Miscellaneous Expenses")
        st.write("Use the (+) button to add dynamic expenses (Marketing, Repairs, etc.)")
        
        exp_data = pd.DataFrame([
            {"Expense Name": "Building Rent", "Amount": 50000, "Explanation": "Monthly fixed rent"},
            {"Expense Name": "Electricity Bill", "Amount": 20000, "Explanation": "Utilities"},
        ])
        
        edited_exp = st.data_editor(exp_data, num_rows="dynamic", key="admin_exp_table", use_container_width=True)
        total_admin_exp = edited_exp['Amount'].sum() if not edited_exp.empty else 0
        st.error(f"Total Operational/Misc Costs: {total_admin_exp} PKR")

    # --- TAB 4: FINAL AUDIT GAUGE ---
    with tabs[3]:
        st.subheader("🏁 Institutional Performance Gauge")
        
        total_income = p_rev + s_rev + c_rev
        total_expenses = (p_rev - p_net) + (s_rev - s_net) + (c_rev - c_net) + total_admin_exp
        net_profit = total_income - total_expenses
        
        # Scoring logic (1-200) based on Profit Margins [cite: 2025-12-29]
        score = max(1, min(200, int((net_profit/total_income)*400))) if total_income > 0 else 1
        
        st.header(f"Strategic Profit Level: {score} / 200")
        st.progress(score / 200)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total School Revenue", f"{total_income} PKR")
        col2.metric("Total Expenses", f"{total_expenses} PKR", delta_color="inverse")
        col3.metric("Final Take-Home Profit", f"{net_profit} PKR")
        
        if score > 150:
            st.success("🌟 Elite Performance: Your institution is highly optimized and profitable.")
        elif score > 100:
            st.warning("⚖️ Healthy: Sustainable operations, but investigate high expense categories.")
        else:
            st.error("🚨 Critical: Low margins. Check Teacher ROI or reduce Admin Expenses.")

    if st.sidebar.button("Logout System"):
        st.session_state.auth = False
        st.rerun()
