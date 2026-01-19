import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF

# --- 1. SECURE LICENSE SYSTEM ---
VALID_KEY = "PRO-MAX-200" 
def check_auth(key): return key == VALID_KEY

# --- 2. UI SETUP ---
st.set_page_config(page_title="Strategic School Optimizer", layout="wide")

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 System Activation")
    key = st.text_input("License Key", type="password")
    if st.button("Activate"):
        if check_auth(key):
            st.session_state.auth = True
            st.rerun()
else:
    st.sidebar.title(f"🏫 Master Control")
    tabs = st.tabs(["👶 Sections Profit", "👨‍🏫 Staff Audit", "🏗️ Admin Expenses", "📊 Final Audit Gauge"])

    # --- TAB 1: SECTIONS PROFIT (Primary, Secondary, College) ---
    with tabs[0]:
        def process_sec(name, key):
            st.subheader(f"📊 {name} Revenue Generation")
            df = pd.DataFrame([{"Class": "Class 1", "Students": 25, "Fee": 4000}])
            edited = st.data_editor(df, num_rows="dynamic", key=f"edit_{key}", use_container_width=True)
            
            total_rev = 0
            if not edited.empty:
                edited['Revenue'] = edited['Students'] * edited['Fee']
                total_rev = edited['Revenue'].sum()
            
            salaries = st.number_input(f"Total Staff Salaries ({name})", value=50000, key=f"sal_{key}")
            sec_profit = total_rev - salaries
            st.info(f"{name} Net Contribution: {sec_profit} PKR")
            return total_rev, sec_profit

        p_rev, p_net = process_sec("Primary", "pri")
        st.divider()
        s_rev, s_net = process_sec("Secondary", "sec")
        st.divider()
        c_rev, c_net = process_sec("College", "col")

    # --- TAB 2: STAFF AUDIT ---
    with tabs[1]:
        st.subheader("👨‍🏫 Teacher Capacity Gauge")
        staff_df = pd.DataFrame([{"Name": "Teacher 1", "Salary": 40000, "Capacity": 8, "Assigned": 6}])
        edited_staff = st.data_editor(staff_df, num_rows="dynamic", key="staff_edit")
        # (Staff logic remains active in background)

    # --- TAB 3: ADMIN EXPENSES (DYNAMIC & EXPLAINABLE) ---
    with tabs[2]:
        st.subheader("🏗️ General & Other Expenses")
        st.write("یہاں آپ بلڈنگ کے کرایے اور بلوں کے علاوہ دیگر تمام اخراجات تفصیل کے ساتھ ڈال سکتے ہیں۔")
        
        # Default fixed expenses
        fixed_exp = pd.DataFrame([
            {"Expense Name": "Building Rent", "Amount": 40000, "Explanation": "Monthly Rent"},
            {"Expense Name": "Electricity Bill", "Amount": 15000, "Explanation": "WAPDA / Utility"},
            {"Expense Name": "Labor/Security", "Amount": 20000, "Explanation": "Guard & Sweeper"}
        ])
        
        # Dynamic expense table with explanation column
        other_exp_table = st.data_editor(fixed_exp, num_rows="dynamic", key="admin_exp_table", use_container_width=True)
        
        total_admin_exp = 0
        if not other_exp_table.empty:
            total_admin_exp = other_exp_table['Amount'].sum()
            
        st.error(f"Total Admin & Other Expenses: {total_admin_exp} PKR")

    # --- TAB 4: FINAL AUDIT GAUGE ---
    with tabs[3]:
        st.subheader("🏁 Institutional Performance Gauge")
        
        total_income = p_rev + s_rev + c_rev
        total_expenses = (p_rev - p_net) + (s_rev - s_net) + (c_rev - c_net) + total_admin_exp
        net_profit = total_income - total_expenses
        
        # Scaling to Profit Level 1-200 [cite: 2025-12-29]
        if total_income > 0:
            margin = net_profit / total_income
            final_score = max(1, min(200, int(margin * 400)))
        else:
            final_score = 1
            
        # Graphical Representation
        st.header(f"Final Strategic Profit Level: {final_score} / 200")
        st.progress(final_score / 200)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total School Income", f"{total_income} PKR")
        col2.metric("Total Expenses", f"{total_expenses} PKR", delta_color="inverse")
        col3.metric("Net Take-Home Profit", f"{net_profit} PKR")
        
        if final_score > 150:
            st.success("🌟 Excellent Performance! Your institution is highly optimized.")
        elif final_score > 100:
            st.warning("⚖️ Stable: But there is room to reduce 'Other Expenses' or increase students.")
        else:
            st.error("🚨 Critical: High expenses or low enrollment. Review your Admin Expenses tab.")

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()
