import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF

# --- 1. SETTINGS & LICENSE ---
MASTER_LICENSE_KEY = "PRO-MAX-200"
SUBSCRIPTION_EXPIRY = datetime.date(2027, 1, 1)

def validate_license(key):
    return key == MASTER_LICENSE_KEY and datetime.date.today() <= SUBSCRIPTION_EXPIRY

# --- 2. SMART ADVICE LOGIC ---
def get_class_advice(students, max_cap):
    if students < 15:
        return "⚠️ Under-populated: Merge Class"
    elif students > max_cap:
        return f"🚨 Over-loaded: Max capacity is {max_cap}. Split now!"
    elif students >= (max_cap - 5):
        return "✅ Near Capacity: Monitor closely"
    else:
        return "✅ Optimized"

def get_teacher_advice(periods):
    if periods < 4: return "🛑 Critical: Under-utilized"
    elif periods < 6: return "⚠️ Action: Increase Load"
    return "✅ Efficient Workload"

# --- 3. PAGE CONFIG ---
st.set_page_config(page_title="Smart Resource Optimizer", layout="wide")

if 'auth' not in st.session_state:
    st.session_state.auth = False

# --- 4. LOGIN ---
if not st.session_state.auth:
    st.title("🔐 System Activation")
    st.subheader("Smart Resource Allocation & Institutional Optimization System")
    school_name = st.text_input("Enter Institution Name")
    key = st.text_input("License Key", type="password")
    if st.button("Activate Dashboard"):
        if validate_license(key):
            st.session_state.auth = True
            st.session_state.school = school_name
            st.rerun()
        else:
            st.error("Invalid Key.")

# --- 5. MAIN DASHBOARD ---
else:
    st.title(f"🏫 {st.session_state.school}")
    
    # PROFIT SCALES (1-200)
    st.markdown("---")
    st.subheader("🚀 Strategic Profit Performance (Scale 1-200)")
    col1, col2, col3 = st.columns(3)
    curr_level = 175 # Dynamic based on your future data
    col1.metric("Previous Level", "85/200")
    col2.metric("Current Profit Level", f"{curr_level}/200", delta="+90")
    col3.metric("Status", "High Efficiency")

    # RESOURCE TABLES
    st.markdown("---")
    tab_t, tab_c = st.tabs(["👨‍🏫 Teacher Efficiency", "🏫 Classroom Capacity Management"])

    with tab_t:
        st.write("### Staff Load Analysis")
        t_data = pd.DataFrame({
            "Teacher Name": ["Staff 1", "Staff 2"],
            "Monthly Salary": [40000, 50000],
            "Periods/Day": [3, 7]
        })
        t_data['System Advice'] = t_data['Periods/Day'].apply(get_teacher_advice)
        st.data_editor(t_data, use_container_width=True, num_rows="dynamic")

    with tab_c:
        st.write("### Classroom Occupancy & Capacity Alerts")
        st.info("Note: Admin can set 'Max Seating Capacity' for each room individually.")
        c_data = pd.DataFrame({
            "Class Name": ["Grade 9", "Grade 10-A", "Grade 10-B"],
            "Current Students": [12, 58, 65],
            "Max Seating Capacity": [40, 60, 60] # Admin sets this
        })
        # Applying the custom capacity logic
        c_data['System Advice'] = c_data.apply(lambda x: get_class_advice(x['Current Students'], x['Max Seating Capacity']), axis=1)
        st.data_editor(c_data, use_container_width=True, num_rows="dynamic")

    # PDF EXPORT
    st.markdown("---")
    if st.button("Finalize & Prepare Report"):
        st.success("Analysis Complete. You can now download the PDF.")
        # PDF logic here...

    if st.sidebar.button("Log Out"):
        st.session_state.auth = False
        st.rerun()
