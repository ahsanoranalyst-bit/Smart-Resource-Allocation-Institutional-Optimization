import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF

# --- 1. SECURE LICENSE SYSTEM ---
VALID_KEY = "PRO-MAX-200" 
def check_auth(key): return key == VALID_KEY

# --- 2. LOGIC FUNCTIONS ---
def analyze_staff_load(row, unit):
    assigned = row['Assigned Periods']
    capacity = row['Teacher Capacity']
    salary = row['Salary']
    if unit == "Daily": m_p = assigned * 26
    elif unit == "Weekly": m_p = assigned * 4
    else: m_p = assigned
    
    cost_per_p = salary / m_p if m_p > 0 else 0
    diff = assigned - capacity
    
    if assigned < capacity: status = f"🛑 Under-filled (Gap: {abs(diff)} p)"; color = "red"
    elif assigned == capacity: status = "✅ Efficient (Ideal)"; color = "green"
    else: status = f"🚨 Overloaded (Extra: {diff} p)"; color = "orange"
    return pd.Series([m_p, round(cost_per_p, 2), status])

# --- 3. UI SETUP ---
st.set_page_config(page_title="Master School Optimizer", layout="wide")

if 'auth' not in st.session_state: st.session_state.auth = False
if 'school_name' not in st.session_state: st.session_state.school_name = ""

# --- LOGIN SCREEN (WITH SCHOOL NAME) ---
if not st.session_state.auth:
    st.title("🔐 System Activation")
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        school_input = st.text_input("Enter School / Institution Name", placeholder="e.g. Allied School")
    with col_l2:
        key_input = st.text_input("Enter License Key", type="password", placeholder="Secret Key")
    
    if st.button("Activate Dashboard"):
        if check_auth(key_input) and school_input:
            st.session_state.auth = True
            st.session_state.school_name = school_input
            st.rerun()
        elif not school_input:
            st.error("Please enter the School Name first.")
        else:
            st.error("Invalid License Key.")

# --- MAIN DASHBOARD ---
else:
    st.sidebar.title(f"🏫 {st.session_state.school_name}")
    st.sidebar.write(f"Date: {datetime.date.today()}")
    
    tabs = st.tabs(["📊 Sections Profit", "👨‍🏫 Teacher Audit", "🏗️ Admin Expenses", "📊 Final Audit Gauge"])

    # --- TAB 1: SECTIONS PROFIT ---
    with tabs[0]:
        def process_sec(name, key):
            st.subheader(f"Section: {name}")
            # Dynamic Class Entry Table
            df = pd.DataFrame([{"Class": "Class 1", "Students": 30, "Fee": 4000}])
            edited = st.data_editor(df, num_rows="dynamic", key=f"edit_{key}", use_container_width=True)
            
            total_rev = 0
            if not edited.empty:
                edited['Revenue'] = edited['Students'] * edited['Fee']
                total_rev = edited['Revenue'].sum()
            
            salaries = st.number_input(f"Total Staff Salaries ({name})", value=50000, key=f"sal_{key}")
            sec_profit = total_rev - salaries
            st.metric(f"{name} Gross Profit", f"{sec_profit} PKR")
            return total_rev, sec_profit

        p_rev, p_net = process_sec("Primary", "pri")
        st.divider()
        s_rev, s_net = process_sec("Secondary", "sec")
        st.divider()
        c_rev, c_net = process_sec("College", "col")

    # --- TAB 2: STAFF AUDIT (CAPACITY GAUGE) ---
    with tabs[1]:
        st.subheader("👨‍🏫 Teacher Capacity & ROI Audit")
        unit = st.radio("Select Unit:", ["Daily", "Weekly", "Monthly"], horizontal=True)
        staff_df = pd.DataFrame([{"Name": "Staff 1", "Salary": 40000, "Teacher Capacity": 8, "Assigned Periods": 6}])
        edited_staff = st.data_editor(staff_df, num_rows="dynamic", key="staff_gauge", use_container_width=True)
        
        if not edited_staff.empty:
            staff_res = edited_staff.apply(lambda row: analyze_staff_load(row, unit), axis=1)
            edited_staff[['Monthly Periods', 'Cost/Period', 'Loading Status']] = staff_res
            st.dataframe(edited_staff, use_container_width=True)

    # --- TAB 3: ADMIN & OTHER EXPENSES (DYNAMIC) ---
    with tabs[2]:
        st.subheader("🏗️ General & Miscellaneous Expenses")
        st.write("Add any additional costs here (e.g. Bills, Repairs, Marketing).")
        
        fixed_exp = pd.DataFrame([
            {"Expense Name": "Building Rent", "Amount": 40000, "Explanation": "Monthly"},
            {"Expense Name": "Electricity", "Amount": 15000, "Explanation": "Wapda Bill"}
        ])
        
        admin_exp_table = st.data_editor(fixed_exp, num_rows="dynamic", key="admin_exp_table", use_container_width=True)
        total_admin_exp = admin_exp_table['Amount'].sum() if not admin_exp_table.empty else 0
        st.error(f"Total Operational Costs: {total_admin_exp} PKR")

    # --- TAB 4: FINAL AUDIT GAUGE ---
    with tabs[3]:
        st.subheader("🏁 Final Performance Audit")
        total_income = p_rev + s_rev + c_rev
        # Total expenses = (Total Rev - Total Net) + Admin Expenses
        total_expenses = (p_rev - p_net) + (s_rev - s_net) + (c_rev - c_net) + total_admin_exp
        net_profit = total_income - total_expenses
        
        # Scoring logic (1-200) [cite: 2025-12-29]
        score = max(1, min(200, int((net_profit/total_income)*400))) if total_income > 0 else 1
        
        st.header(f"Strategic Profit Level: {score} / 200")
        st.progress(score / 200)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total School Income", f"{total_income} PKR")
        col2.metric("Total Expenses", f"{total_expenses} PKR", delta_color="inverse")
        col3.metric("Net Take-Home Profit", f"{net_profit} PKR")

    if st.sidebar.button("Logout & Reset"):
        st.session_state.auth = False
        st.rerun()
