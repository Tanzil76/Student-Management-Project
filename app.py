import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

# ----------------------------------------------------------------------------
# Persistence
# ----------------------------------------------------------------------------
DATABASE = "school_data.json"


def load_data():
    if Path(DATABASE).exists():
        with open(DATABASE, "r") as f:
            content = f.read()
            if content:
                return json.loads(content)
    return {"students": [], "teachers": []}


def save(data):
    with open(DATABASE, "w") as f:
        json.dump(data, f, indent=4)


if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data


# ----------------------------------------------------------------------------
# Domain classes (same logic as the original script, adapted for Streamlit)
# ----------------------------------------------------------------------------
class Persons(ABC):
    @abstractmethod
    def get_role(self):
        pass

    @staticmethod
    def validate_email(email):
        return "@" in email and "." in email


class Student(Persons):
    def get_role(self):
        return "Student"

    def register(self, name, age, email, roll_no):
        if not Persons.validate_email(email):
            return False, "Invalid email address."
        for s in data["students"]:
            if s["roll_no"] == roll_no:
                return False, "A student with that roll number already exists."
        data["students"].append(
            {"name": name, "age": age, "email": email, "roll_no": roll_no, "grades": {}}
        )
        save(data)
        return True, f"Student '{name}' registered successfully."

    def add_grade(self, roll_no, subject, marks):
        for s in data["students"]:
            if s["roll_no"] == roll_no:
                s["grades"][subject] = marks
                save(data)
                return True, f"Grade added for {s['name']} in {subject}."
        return False, "Student not found."

    def find(self, roll_no):
        for s in data["students"]:
            if s["roll_no"] == roll_no:
                return s
        return None


class Teacher(Persons):
    def get_role(self):
        return "Teacher"

    def register(self, name, age, email, subject, emp_id):
        if not Persons.validate_email(email):
            return False, "Invalid email address."
        for t in data["teachers"]:
            if t["emp_id"] == emp_id:
                return False, "A teacher with that employee ID already exists."
        data["teachers"].append(
            {"name": name, "age": age, "email": email, "subject": subject, "emp_id": emp_id}
        )
        save(data)
        return True, f"Teacher '{name}' registered successfully."

    def find(self, emp_id):
        for t in data["teachers"]:
            if t["emp_id"] == emp_id:
                return t
        return None


stud = Student()
tech = Teacher()

# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(page_title="Student Management", page_icon=":mortar_board:", layout="wide")

# ----------------------------------------------------------------------------
# CSS — light SaaS admin dashboard look
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        .stApp { background: #f4f6fb; }
        div.block-container { padding-top: 1.1rem; padding-bottom: 3rem; max-width: 1300px; }

        /* Top bar */
        .topbar {
            display: flex; justify-content: space-between; align-items: center;
            background: #ffffff; border-radius: 14px; padding: 0.9rem 1.4rem;
            box-shadow: 0 2px 10px rgba(17,24,39,0.06);
            margin-bottom: 1.3rem; border: 1px solid #eef0f5;
        }
        .topbar-crumb { font-weight: 700; color: #111827; font-size: 1.05rem; }
        .topbar-right { display: flex; align-items: center; gap: 1.1rem; color: #6b7280; font-size: 0.85rem; }
        .avatar-badge {
            width: 34px; height: 34px; border-radius: 50%; background: #1e293b; color: #fff;
            display: inline-flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.8rem;
        }

        /* Greeting */
        .greet-title { font-size: 1.55rem; font-weight: 800; color: #111827; margin-bottom: 0.1rem; }
        .greet-sub { color: #6b7280; margin-bottom: 1.1rem; }

        /* Stat cards */
        .stat-card {
            border-radius: 16px; padding: 1.15rem 1.3rem; height: 100%;
            box-shadow: 0 2px 10px rgba(17,24,39,0.05); border: 1px solid rgba(0,0,0,0.03);
        }
        .stat-icon {
            width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center;
            justify-content: center; font-size: 1.25rem; margin-bottom: 0.6rem;
        }
        .stat-label { color: #4b5563; font-size: 0.88rem; font-weight: 600; }
        .stat-value { font-size: 1.75rem; font-weight: 800; color: #111827; margin: 0.1rem 0 0.2rem 0; }
        .stat-delta { font-size: 0.78rem; font-weight: 600; }
        .blue   { background: #eaf2ff; } .blue .stat-icon   { background: #cfe2ff; color: #2f6fed; } .blue .stat-delta { color: #2f6fed; }
        .green  { background: #eafaf0; } .green .stat-icon  { background: #cdf3dc; color: #16a34a; } .green .stat-delta { color: #16a34a; }
        .purple { background: #f3edfd; } .purple .stat-icon { background: #e2d5fb; color: #7c3aed; } .purple .stat-delta { color: #7c3aed; }
        .orange { background: #fff6e5; } .orange .stat-icon { background: #fde9bd; color: #d97706; } .orange .stat-delta { color: #d97706; }

        /* Panels */
        .panel {
            background: #ffffff; border-radius: 16px; padding: 1.3rem 1.4rem;
            box-shadow: 0 2px 10px rgba(17,24,39,0.05); border: 1px solid #eef0f5; height: 100%;
        }
        .panel-title { font-weight: 700; color: #111827; font-size: 1.05rem; margin-bottom: 0.9rem; }

        /* Status pill */
        .pill { padding: 0.15rem 0.65rem; border-radius: 999px; font-size: 0.78rem; font-weight: 700; }
        .pill-active { background: #dcfce7; color: #16a34a; }
        .pill-new { background: #fee2e2; color: #dc2626; }

        /* Quick action buttons */
        .stButton>button {
            border-radius: 10px; font-weight: 600; text-align: left;
        }
        button[kind="secondary"] { border: 1px solid #e5e7eb !important; }

        /* Top performer row */
        .perf-row { display: flex; align-items: center; gap: 0.8rem; padding: 0.55rem 0; border-bottom: 1px solid #f1f2f6; }
        .perf-rank {
            width: 34px; height: 34px; border-radius: 10px; background: #eaf2ff; color: #2f6fed;
            display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.85rem; flex-shrink: 0;
        }
        .perf-name { font-weight: 700; color: #111827; font-size: 0.9rem; }
        .perf-sub { color: #9ca3af; font-size: 0.76rem; }

        /* Sub-nav pills (Directory / Register / Lookup) */
        div[role="radiogroup"] { gap: 0.4rem; }
        div[role="radiogroup"] label {
            background: #ffffff; border: 1px solid #e5e7eb; padding: 0.35rem 0.9rem !important;
            border-radius: 999px !important; margin-right: 0.3rem;
        }

        /* Dataframe */
        div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid #eef0f5; }

        section[data-testid="stSidebar"] { background: #0f172a; }
        section[data-testid="stSidebar"] .block-container { padding-top: 1.2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Sidebar navigation
# ----------------------------------------------------------------------------
PAGES = ["Dashboard", "Students", "Faculty", "Grades", "Settings"]
ICONS = ["speedometer2", "people-fill", "person-badge-fill", "star-fill", "gear-fill"]

if "manual_select" not in st.session_state:
    st.session_state.manual_select = None
if "sub_tab" not in st.session_state:
    st.session_state.sub_tab = {}

with st.sidebar:
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:0.6rem;padding:0.4rem 0.2rem 1rem 0.2rem;
                    border-bottom:1px solid rgba(255,255,255,0.08);margin-bottom:0.8rem;">
            <div style="width:42px;height:42px;border-radius:12px;background:#2f6fed;
                        display:flex;align-items:center;justify-content:center;font-size:1.3rem;">🎓</div>
            <div>
                <div style="color:#f9fafb;font-weight:800;font-size:1.02rem;line-height:1.1;">Student Management</div>
                <div style="color:#8b93a7;font-size:0.72rem;">Learn • Grow • Succeed</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected = option_menu(
        menu_title=None,
        options=PAGES,
        icons=ICONS,
        manual_select=st.session_state.manual_select,
        default_index=0,
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"color": "#9aa4bf", "font-size": "16px"},
            "nav-link": {
                "font-size": "0.92rem", "font-weight": "600", "color": "#c7cede",
                "border-radius": "10px", "margin": "3px 0", "padding": "0.55rem 0.8rem",
            },
            "nav-link-selected": {"background-color": "#2f6fed", "color": "#ffffff"},
        },
        key="main_menu",
    )
    st.session_state.manual_select = None

    st.markdown(
        """
        <div style="margin-top:2.2rem;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                    border-radius:12px;padding:0.9rem;text-align:center;">
            <div style="font-size:1.1rem;">🎓</div>
            <div style="color:#e5e7eb;font-style:italic;font-size:0.82rem;margin-top:0.3rem;">
                "Better Education<br>for a Brighter Future"
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------------
# Top bar
# ----------------------------------------------------------------------------
now = datetime.now()
st.markdown(
    f"""
    <div class="topbar">
        <div class="topbar-crumb">{selected}</div>
        <div class="topbar-right">
            <span>📅 {now.strftime('%a, %d %b %Y')}</span>
            <span>🕒 {now.strftime('%I:%M %p')}</span>
            <span class="avatar-badge">AD</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


def stat_card(col, color, icon, label, value, delta):
    with col:
        st.markdown(
            f"""
            <div class="stat-card {color}">
                <div class="stat-icon">{icon}</div>
                <div class="stat-label">{label}</div>
                <div class="stat-value">{value}</div>
                <div class="stat-delta">{delta}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def goto(page, tab=None):
    st.session_state.manual_select = PAGES.index(page)
    if tab:
        st.session_state.sub_tab[page] = tab
    st.rerun()


# ----------------------------------------------------------------------------
# Dashboard
# ----------------------------------------------------------------------------
if selected == "Dashboard":
    total_students = len(data["students"])
    total_teachers = len(data["teachers"])
    subjects = set()
    for s in data["students"]:
        subjects.update(s["grades"].keys())
    for t in data["teachers"]:
        subjects.add(t["subject"])
    total_subjects = len(subjects)
    total_grades = sum(len(s["grades"]) for s in data["students"])

    st.markdown('<div class="greet-title">Good Morning, Admin! 👋</div>', unsafe_allow_html=True)
    st.markdown('<div class="greet-sub">Here\'s what\'s happening with your school today.</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    stat_card(c1, "blue", "👨‍🎓", "Total Students", total_students, f"{total_students} enrolled")
    stat_card(c2, "green", "📚", "Subjects Tracked", total_subjects, "across grades & faculty")
    stat_card(c3, "purple", "👩‍🏫", "Total Faculty", total_teachers, f"{total_teachers} registered")
    stat_card(c4, "orange", "📝", "Grades Recorded", total_grades, "entries logged")

    st.write("")
    col_left, col_right = st.columns([2, 1])

    with col_left:
        row1, row2 = st.columns(2)

        with row1:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">Student Enrollment Over Time</div>', unsafe_allow_html=True)
            if data["students"]:
                y = list(range(1, len(data["students"]) + 1))
                x = [s["name"] for s in data["students"]]
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=x, y=y, mode="lines+markers", line=dict(color="#2f6fed", width=3),
                    fill="tozeroy", fillcolor="rgba(47,111,237,0.12)", marker=dict(size=6, color="#2f6fed"),
                ))
                fig.update_layout(
                    height=280, margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#f1f2f6"),
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Register students to see enrollment trends.")
            st.markdown("</div>", unsafe_allow_html=True)

        with row2:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">Students by Grade Band</div>', unsafe_allow_html=True)
            bands = {"A (90+)": 0, "B (80-89)": 0, "C (70-79)": 0, "D (60-69)": 0, "F (<60)": 0}
            for s in data["students"]:
                if s["grades"]:
                    avg = sum(s["grades"].values()) / len(s["grades"])
                    if avg >= 90: bands["A (90+)"] += 1
                    elif avg >= 80: bands["B (80-89)"] += 1
                    elif avg >= 70: bands["C (70-79)"] += 1
                    elif avg >= 60: bands["D (60-69)"] += 1
                    else: bands["F (<60)"] += 1
            if any(bands.values()):
                colors = ["#2f6fed", "#16a34a", "#f59e0b", "#7c3aed", "#e11d48"]
                fig2 = go.Figure(data=[go.Pie(
                    labels=list(bands.keys()), values=list(bands.values()), hole=0.62,
                    marker=dict(colors=colors), textinfo="none",
                )])
                fig2.update_layout(
                    height=280, margin=dict(l=10, r=10, t=10, b=10), showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)",
                    annotations=[dict(text=f"{total_students}<br>Students", x=0.5, y=0.5, font_size=14, showarrow=False)],
                )
                cchart, clegend = st.columns([1.3, 1])
                with cchart:
                    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
                with clegend:
                    for (label, val), color in zip(bands.items(), colors):
                        st.markdown(
                            f'<div style="display:flex;align-items:center;gap:0.4rem;margin:0.35rem 0;font-size:0.82rem;">'
                            f'<span style="width:9px;height:9px;border-radius:50%;background:{color};display:inline-block;"></span>'
                            f'{label} <b style="margin-left:auto;">{val}</b></div>',
                            unsafe_allow_html=True,
                        )
            else:
                st.info("No grades recorded yet.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.write("")
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        rc1, rc2 = st.columns([3, 1])
        rc1.markdown('<div class="panel-title">Recent Students</div>', unsafe_allow_html=True)
        if rc2.button("View All →", use_container_width=True):
            goto("Students", "Directory")
        if data["students"]:
            rows = []
            for s in data["students"][-5:][::-1]:
                grades = s["grades"]
                status = "Active" if grades else "New"
                rows.append({
                    "ID": s["roll_no"], "Name": s["name"], "Email": s["email"],
                    "Age": s["age"], "Subjects": len(grades), "Status": status,
                })
            df = pd.DataFrame(rows)
            st.dataframe(
                df, use_container_width=True, hide_index=True,
                column_config={"Status": st.column_config.TextColumn("Status")},
            )
        else:
            st.info("No students registered yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Quick Actions</div>', unsafe_allow_html=True)
        if st.button("➕  Add New Student", use_container_width=True):
            goto("Students", "Register New")
        if st.button("📝  Add Grade", use_container_width=True):
            goto("Grades")
        if st.button("👩‍🏫  Add Faculty", use_container_width=True):
            goto("Faculty", "Register New")
        if st.button("📊  View Directory", use_container_width=True):
            goto("Students", "Directory")
        st.markdown("</div>", unsafe_allow_html=True)

        st.write("")
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        tc1, tc2 = st.columns([3, 1])
        tc1.markdown('<div class="panel-title">Top Performers</div>', unsafe_allow_html=True)
        ranked = sorted(
            [s for s in data["students"] if s["grades"]],
            key=lambda s: sum(s["grades"].values()) / len(s["grades"]),
            reverse=True,
        )[:5]
        if ranked:
            for i, s in enumerate(ranked, start=1):
                avg = sum(s["grades"].values()) / len(s["grades"])
                st.markdown(
                    f"""
                    <div class="perf-row">
                        <div class="perf-rank">#{i}</div>
                        <div>
                            <div class="perf-name">{s['name']}</div>
                            <div class="perf-sub">Roll No {s['roll_no']} · Avg {avg:.1f}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No grades yet.")
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Students
# ----------------------------------------------------------------------------
elif selected == "Students":
    default_tab = st.session_state.sub_tab.pop("Students", "Directory")
    tabs = ["Directory", "Register New", "Lookup"]
    tab = st.radio("Students view", tabs, index=tabs.index(default_tab), horizontal=True, label_visibility="collapsed")

    st.write("")
    if tab == "Directory":
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">All Students</div>', unsafe_allow_html=True)
        if data["students"]:
            rows = []
            for s in data["students"]:
                grades = s["grades"]
                avg = sum(grades.values()) / len(grades) if grades else 0
                rows.append({
                    "Roll No": s["roll_no"], "Name": s["name"], "Age": s["age"], "Email": s["email"],
                    "Subjects Graded": len(grades), "Average": round(avg, 1),
                    "Status": "Active" if grades else "New",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No students registered yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    elif tab == "Register New":
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Register a New Student</div>', unsafe_allow_html=True)
        with st.form("register_student_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name")
                age = st.number_input("Age", min_value=3, max_value=100, step=1)
            with c2:
                email = st.text_input("Email")
                roll_no = st.text_input("Roll Number")
            submitted = st.form_submit_button("Register Student", use_container_width=True)
        if submitted:
            if not name or not roll_no or not email:
                st.error("Please fill in all fields.")
            else:
                ok, msg = stud.register(name, int(age), email, roll_no)
                st.success(msg) if ok else st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Look Up a Student</div>', unsafe_allow_html=True)
        roll_no = st.text_input("Enter Roll Number")
        if st.button("Search", use_container_width=True) and roll_no:
            s = stud.find(roll_no)
            if s:
                grades = s["grades"]
                avg = sum(grades.values()) / len(grades) if grades else 0
                c1, c2, c3 = st.columns(3)
                c1.metric("Name", s["name"])
                c2.metric("Roll No", s["roll_no"])
                c3.metric("Average", f"{avg:.1f}")
                st.write(f"**Age:** {s['age']}  \n**Email:** {s['email']}")
                if grades:
                    st.dataframe(pd.DataFrame(list(grades.items()), columns=["Subject", "Marks"]),
                                 use_container_width=True, hide_index=True)
                else:
                    st.info("No grades recorded yet.")
            else:
                st.error("Student not found.")
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Faculty
# ----------------------------------------------------------------------------
elif selected == "Faculty":
    default_tab = st.session_state.sub_tab.pop("Faculty", "Directory")
    tabs = ["Directory", "Register New", "Lookup"]
    tab = st.radio("Faculty view", tabs, index=tabs.index(default_tab), horizontal=True, label_visibility="collapsed")

    st.write("")
    if tab == "Directory":
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">All Faculty</div>', unsafe_allow_html=True)
        if data["teachers"]:
            rows = [{"Emp ID": t["emp_id"], "Name": t["name"], "Age": t["age"],
                     "Email": t["email"], "Subject": t["subject"]} for t in data["teachers"]]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No teachers registered yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    elif tab == "Register New":
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Register a New Teacher</div>', unsafe_allow_html=True)
        with st.form("register_teacher_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name")
                age = st.number_input("Age", min_value=18, max_value=100, step=1)
                subject = st.text_input("Subject Taught")
            with c2:
                email = st.text_input("Email")
                emp_id = st.text_input("Employee ID")
            submitted = st.form_submit_button("Register Teacher", use_container_width=True)
        if submitted:
            if not name or not emp_id or not email or not subject:
                st.error("Please fill in all fields.")
            else:
                ok, msg = tech.register(name, int(age), email, subject, emp_id)
                st.success(msg) if ok else st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Look Up a Teacher</div>', unsafe_allow_html=True)
        emp_id = st.text_input("Enter Employee ID")
        if st.button("Search", use_container_width=True) and emp_id:
            t = tech.find(emp_id)
            if t:
                c1, c2, c3 = st.columns(3)
                c1.metric("Name", t["name"])
                c2.metric("Emp ID", t["emp_id"])
                c3.metric("Subject", t["subject"])
                st.write(f"**Age:** {t['age']}  \n**Email:** {t['email']}")
            else:
                st.error("Teacher not found.")
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Grades
# ----------------------------------------------------------------------------
elif selected == "Grades":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Add a Grade for a Student</div>', unsafe_allow_html=True)
    if not data["students"]:
        st.info("No students registered yet. Register a student first.")
    else:
        roll_options = {f"{s['name']} ({s['roll_no']})": s["roll_no"] for s in data["students"]}
        with st.form("add_grade_form", clear_on_submit=True):
            selected_student = st.selectbox("Student", list(roll_options.keys()))
            c1, c2 = st.columns(2)
            with c1:
                subject = st.text_input("Subject")
            with c2:
                marks = st.number_input("Marks", min_value=0.0, max_value=100.0, step=0.5)
            submitted = st.form_submit_button("Add Grade", use_container_width=True)
        if submitted:
            if not subject:
                st.error("Please enter a subject.")
            else:
                ok, msg = stud.add_grade(roll_options[selected_student], subject, marks)
                st.success(msg) if ok else st.error(msg)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">All Recorded Grades</div>', unsafe_allow_html=True)
    grade_rows = []
    for s in data["students"]:
        for subj, marks in s["grades"].items():
            grade_rows.append({"Roll No": s["roll_no"], "Name": s["name"], "Subject": subj, "Marks": marks})
    if grade_rows:
        st.dataframe(pd.DataFrame(grade_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No grades recorded yet.")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------------
elif selected == "Settings":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Data & Storage</div>', unsafe_allow_html=True)
    st.write(f"**Database file:** `{DATABASE}`")
    st.write(f"**Total students:** {len(data['students'])}  |  **Total teachers:** {len(data['teachers'])}")
    st.download_button(
        "⬇️ Download data as JSON",
        data=json.dumps(data, indent=4),
        file_name="school_data.json",
        mime="application/json",
        use_container_width=True,
    )
    with st.expander("View raw data"):
        st.json(data)
    st.markdown("</div>", unsafe_allow_html=True)