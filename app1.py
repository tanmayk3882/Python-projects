import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# ---------- CONFIG ----------
USERNAME = "JayFulaware"
PASSWORD = "jay1111"
EXCEL_FILE = "students.xlsx"

BRANCH_SUBJECTS = {
    "AIML": ["Python", "DSA", "ML Algo", "DL"],
    "CS": ["C", "C++", "Java", "Python", "DSA", "OS", "DBMS", "CN", "WebDev"],
    "IT": ["C", "C++", "Java", "Python", "DSA", "OS", "DBMS", "CN", "WebDev"],
    "Civil": ["Engg Mech", "Bldg Materials", "Surveying", "Hydraulics", "Struct Design"],
    "Electrical": ["Circuits", "Electronics", "PowerSys", "Machines", "CtrlSys"],
}

COLUMNS = ["Timestamp", "Branch", "Student Name", "Roll No", "Enrollment No", "Subject", "Marks"]

# ---------- STORAGE ----------
def init_excel():
    if not os.path.exists(EXCEL_FILE):
        pd.DataFrame(columns=COLUMNS).to_excel(EXCEL_FILE, index=False)

def append_rows(rows):
    init_excel()
    df = pd.read_excel(EXCEL_FILE)
    df = pd.concat([df, pd.DataFrame(rows, columns=COLUMNS)], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

def load_all():
    init_excel()
    return pd.read_excel(EXCEL_FILE)

def delete_group(timestamp_val, enrollment_val):
    """Delete all rows that belong to one saved entry (same Timestamp + Enrollment)."""
    df = load_all()
    before = len(df)
    df = df[~((df["Timestamp"] == timestamp_val) & (df["Enrollment No"] == enrollment_val))]
    df.to_excel(EXCEL_FILE, index=False)
    return len(df) < before

# ---------- STATE ----------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "branch" not in st.session_state:
    st.session_state.branch = None

def go(page):
    st.session_state.page = page

def logout():
    st.session_state.logged_in = False
    st.session_state.branch = None
    go("home")

# ---------- PAGES ----------
def page_home():
    st.title("Dilkap College Polytechnic")
    st.caption("Student Exam Database")
    st.divider()
    if st.button("Enter →", use_container_width=True):
        go("login")

def page_login():
    st.title("Login")
    st.caption("Only authorized users can continue")
    st.divider()

    with st.form("login_form", clear_on_submit=False):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        login_clicked = st.form_submit_button("Login")

    if login_clicked:
        if u == USERNAME and p == PASSWORD:
            st.session_state.logged_in = True
            go("dashboard")
            st.success("Logged in ✅")
        else:
            st.error("Invalid username or password")

    if st.button("← Back"):
        go("home")

def page_dashboard():
    st.title("Dashboard")
    st.caption("Choose your branch and enter marks")
    st.divider()

    # Branch selection
    st.session_state.branch = st.radio("Branch", list(BRANCH_SUBJECTS.keys()), horizontal=True)

    st.subheader(f"Enter Student Details — {st.session_state.branch}")
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Student Name")
    with col2:
        roll = st.text_input("Roll No")
    with col3:
        enroll = st.text_input("Enrollment No")

    st.subheader("Subject Marks")
    marks = {}
    for subj in BRANCH_SUBJECTS[st.session_state.branch]:
        marks[subj] = st.number_input(f"{subj} Marks", min_value=0, max_value=100, step=1)

    save = st.button("Save to Excel")
    if save:
        if not name or not roll or not enroll:
            st.error("Name, Roll No, and Enrollment No are required.")
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rows = [
                [now, st.session_state.branch, name, roll, enroll, subj, m]
                for subj, m in marks.items()
            ]
            append_rows(rows)
            st.success("Saved to Excel ✅")

    st.divider()

    # ---------- PROFESSIONAL TABLE + DELETE BUTTON ----------
    st.subheader("View & Manage Records")

    df = load_all()
    if df.empty:
        st.info("No records yet. Add some above.")
    else:
        # Build a grouped/pretty table: one row per saved student entry
        grouped = (
            df.groupby(["Timestamp", "Branch", "Student Name", "Roll No", "Enrollment No"], dropna=False)
              .apply(lambda g: " | ".join(f"{row.Subject}:{int(row.Marks)}" if pd.notna(row.Marks) else f"{row.Subject}:–"
                                          for _, row in g.iterrows()))
              .reset_index(name="Subjects & Marks")
        )

        # Render a header row
        header_cols = st.columns([2, 1.2, 2, 1.2, 1.8, 3, 0.8])
        header_cols[0].markdown("**Timestamp**")
        header_cols[1].markdown("**Branch**")
        header_cols[2].markdown("**Student Name**")
        header_cols[3].markdown("**Roll No**")
        header_cols[4].markdown("**Enrollment No**")
        header_cols[5].markdown("**Subjects & Marks**")
        header_cols[6].markdown("**Action**")

        # zebra rows
        for i, row in grouped.iterrows():
            bg = "#f6f8fa" if i % 2 == 0 else "#ffffff"
            with st.container():
                cols = st.columns([2, 1.2, 2, 1.2, 1.8, 3, 0.8], gap="small")
                cols[0].markdown(f"<div style='background:{bg}; padding:8px; border-radius:6px'>{row['Timestamp']}</div>", unsafe_allow_html=True)
                cols[1].markdown(f"<div style='background:{bg}; padding:8px; border-radius:6px'>{row['Branch']}</div>", unsafe_allow_html=True)
                cols[2].markdown(f"<div style='background:{bg}; padding:8px; border-radius:6px'>{row['Student Name']}</div>", unsafe_allow_html=True)
                cols[3].markdown(f"<div style='background:{bg}; padding:8px; border-radius:6px'>{row['Roll No']}</div>", unsafe_allow_html=True)
                cols[4].markdown(f"<div style='background:{bg}; padding:8px; border-radius:6px'>{row['Enrollment No']}</div>", unsafe_allow_html=True)
                cols[5].markdown(f"<div style='background:{bg}; padding:8px; border-radius:6px; white-space:pre-wrap'>{row['Subjects & Marks']}</div>", unsafe_allow_html=True)

                # nicer delete button
                if cols[6].button("🗑️", key=f"del_{i}", help="Delete this entry"):
                    ok = delete_group(row["Timestamp"], row["Enrollment No"])
                    if ok:
                        st.toast("Deleted", icon="🗑️")
                        st.rerun()
                    else:
                        st.error("Could not delete. Try again.")

    st.divider()

    colA, colB, colC = st.columns(3)
    with colA:
        if st.button("Home"):
            go("home")
    with colB:
        if st.button("Logout"):
            logout()
    with colC:
        df = load_all()
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)
        st.download_button(
            "Download Excel",
            data=buffer,
            file_name="students.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ---------- ROUTER ----------
init_excel()

if not st.session_state.logged_in:
    if st.session_state.page == "home":
        page_home()
    else:
        page_login()
else:
    page_dashboard()