import json
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd
import streamlit as st

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
# Domain classes (same logic as the original script, adapted for Streamlit
# forms instead of blocking input() calls)
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
st.set_page_config(page_title="School Management System", page_icon=":school:", layout="wide")

# ----------------------------------------------------------------------------
# Classic, embossed / 3-D styling
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Source+Sans+3:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] { font-family: 'Source Sans 3', sans-serif; }

        .stApp {
            background: radial-gradient(circle at 20% 0%, #f3ede0 0%, #e8e1d3 45%, #ddd4c1 100%);
        }
        div.block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1200px; }

        /* ---- Letterhead banner ---- */
        .letterhead {
            background: linear-gradient(160deg, #1c2b4a 0%, #16213a 55%, #0f172a 100%);
            border-radius: 16px;
            padding: 1.6rem 2.2rem;
            margin-bottom: 1.6rem;
            box-shadow:
                0 10px 20px rgba(15, 23, 42, 0.35),
                0 2px 0 rgba(255,255,255,0.06) inset,
                0 -6px 14px rgba(0,0,0,0.25) inset;
            border: 1px solid #2b3b5e;
            position: relative;
            overflow: hidden;
        }
        .letterhead::before {
            content: "";
            position: absolute; inset: 0;
            background: linear-gradient(120deg, rgba(212,175,55,0.10), transparent 40%);
        }
        .app-title {
            font-family: 'Playfair Display', serif;
            font-size: 2.3rem;
            font-weight: 800;
            color: #f4e9c9;
            margin: 0;
            letter-spacing: 0.3px;
            text-shadow: 0 2px 3px rgba(0,0,0,0.5);
        }
        .app-subtitle {
            color: #b9c2d6;
            margin-top: 0.35rem;
            margin-bottom: 0;
            font-size: 0.98rem;
        }
        .app-divider {
            height: 3px;
            width: 64px;
            background: linear-gradient(90deg, #d4af37, #f4e9c9);
            border-radius: 3px;
            margin-top: 0.7rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.4);
        }

        /* ---- Section headers ---- */
        h1, h2, h3, div[data-testid="stMarkdownContainer"] h3 {
            font-family: 'Playfair Display', serif !important;
            color: #1c2b4a !important;
        }

        /* ---- 3-D bordered cards (st.container(border=True)) ---- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(180deg, #ffffff 0%, #f7f4ec 100%) !important;
            border-radius: 16px !important;
            border: 1px solid #d8cfb8 !important;
            box-shadow:
                0 14px 28px rgba(28, 43, 74, 0.12),
                0 2px 4px rgba(28, 43, 74, 0.10),
                0 1px 0 rgba(255,255,255,0.7) inset !important;
            padding: 0.5rem 0.4rem !important;
        }

        /* ---- Metric cards ---- */
        div[data-testid="stMetric"] {
            background: linear-gradient(160deg, #ffffff 0%, #f2ede1 100%);
            border-radius: 14px;
            padding: 1rem 1.2rem;
            border: 1px solid #ddd2b5;
            box-shadow:
                0 10px 18px rgba(28, 43, 74, 0.12),
                0 1px 0 rgba(255,255,255,0.8) inset;
        }
        div[data-testid="stMetricLabel"] { color: #6b5f43 !important; font-weight: 600; }
        div[data-testid="stMetricValue"] { color: #1c2b4a !important; font-family: 'Playfair Display', serif; }

        /* ---- Buttons: brass / embossed look ---- */
        .stButton>button, .stFormSubmitButton>button {
            border-radius: 10px;
            font-weight: 700;
            letter-spacing: 0.2px;
            color: #2a2110;
            background: linear-gradient(180deg, #f6e6b4 0%, #d4af37 55%, #b8912a 100%);
            border: 1px solid #9c7b23;
            box-shadow:
                0 6px 12px rgba(120, 90, 20, 0.35),
                0 1px 0 rgba(255,255,255,0.6) inset,
                0 -3px 6px rgba(0,0,0,0.15) inset;
            transition: transform 0.08s ease, box-shadow 0.08s ease;
        }
        .stButton>button:hover, .stFormSubmitButton>button:hover {
            transform: translateY(-1px);
            box-shadow:
                0 9px 16px rgba(120, 90, 20, 0.40),
                0 1px 0 rgba(255,255,255,0.6) inset;
            color: #1c1608;
        }
        .stButton>button:active, .stFormSubmitButton>button:active {
            transform: translateY(1px);
            box-shadow: 0 3px 6px rgba(120, 90, 20, 0.30) inset;
        }

        /* ---- Inputs: inset / carved look ---- */
        .stTextInput input, .stNumberInput input, div[data-baseweb="select"] > div {
            border-radius: 8px !important;
            border: 1px solid #cfc4a4 !important;
            background: #fbf9f3 !important;
            box-shadow: 0 2px 4px rgba(28,43,74,0.08) inset !important;
        }

        /* ---- Tabs ---- */
        button[data-baseweb="tab"] { font-weight: 600; color: #6b5f43; }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #1c2b4a !important;
            border-bottom: 3px solid #d4af37 !important;
        }

        /* ---- Dataframe ---- */
        div[data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 16px rgba(28,43,74,0.12);
            border: 1px solid #ddd2b5;
        }

        /* ---- Sidebar: dark walnut / navy panel ---- */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #14213d 0%, #0d1526 100%);
            box-shadow: 4px 0 14px rgba(0,0,0,0.35);
        }
        section[data-testid="stSidebar"] * { color: #e7e2d0 !important; }
        section[data-testid="stSidebar"] h2 {
            font-family: 'Playfair Display', serif !important;
            color: #f4e9c9 !important;
        }
        section[data-testid="stSidebar"] label[data-baseweb="radio"] {
            padding: 0.35rem 0.5rem;
            border-radius: 8px;
        }
        section[data-testid="stSidebar"] label[data-baseweb="radio"]:hover {
            background: rgba(212,175,55,0.12);
        }
        section[data-testid="stSidebar"] hr { border-color: rgba(231,226,208,0.15) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Sidebar navigation
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## \U0001F393 School Manager")
    st.caption("Students  •  Teachers  •  Grades")
    st.markdown("---")
    page = st.radio(
        "Navigate to",
        [
            "Dashboard",
            "Register Student",
            "Register Teacher",
            "Add Grade",
            "Student Details",
            "Teacher Details",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption(f"Data file: `{DATABASE}`")

st.markdown(
    """
    <div class="letterhead">
        <p class="app-title">School Management System</p>
        <p class="app-subtitle">A classic ledger-style dashboard for managing students, teachers and grades.</p>
        <div class="app-divider"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Dashboard
# ----------------------------------------------------------------------------
if page == "Dashboard":
    total_students = len(data["students"])
    total_teachers = len(data["teachers"])
    all_grades = [m for s in data["students"] for m in s["grades"].values()]
    avg_grade = sum(all_grades) / len(all_grades) if all_grades else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Students", total_students)
    col2.metric("Total Teachers", total_teachers)
    col3.metric("Average Grade", f"{avg_grade:.1f}")

    st.write("")
    with st.container(border=True):
        tab1, tab2 = st.tabs(["Students", "Teachers"])

        with tab1:
            if data["students"]:
                rows = []
                for s in data["students"]:
                    grades = s["grades"]
                    avg = sum(grades.values()) / len(grades) if grades else 0
                    rows.append(
                        {
                            "Roll No": s["roll_no"],
                            "Name": s["name"],
                            "Age": s["age"],
                            "Email": s["email"],
                            "Subjects Graded": len(grades),
                            "Average": round(avg, 1),
                        }
                    )
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.info("No students registered yet.")

        with tab2:
            if data["teachers"]:
                rows = [
                    {
                        "Emp ID": t["emp_id"],
                        "Name": t["name"],
                        "Age": t["age"],
                        "Email": t["email"],
                        "Subject": t["subject"],
                    }
                    for t in data["teachers"]
                ]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.info("No teachers registered yet.")

# ----------------------------------------------------------------------------
# Register Student
# ----------------------------------------------------------------------------
elif page == "Register Student":
    st.subheader("Register a New Student")
    with st.container(border=True):
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

# ----------------------------------------------------------------------------
# Register Teacher
# ----------------------------------------------------------------------------
elif page == "Register Teacher":
    st.subheader("Register a New Teacher")
    with st.container(border=True):
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

# ----------------------------------------------------------------------------
# Add Grade
# ----------------------------------------------------------------------------
elif page == "Add Grade":
    st.subheader("Add a Grade for a Student")
    if not data["students"]:
        st.info("No students registered yet. Register a student first.")
    else:
        roll_options = {f"{s['name']} ({s['roll_no']})": s["roll_no"] for s in data["students"]}
        with st.container(border=True):
            with st.form("add_grade_form", clear_on_submit=True):
                selected = st.selectbox("Student", list(roll_options.keys()))
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
                ok, msg = stud.add_grade(roll_options[selected], subject, marks)
                st.success(msg) if ok else st.error(msg)

# ----------------------------------------------------------------------------
# Student Details
# ----------------------------------------------------------------------------
elif page == "Student Details":
    st.subheader("Look Up a Student")
    with st.container(border=True):
        roll_no = st.text_input("Enter Roll Number")
        search = st.button("Search", use_container_width=True)

    if search and roll_no:
        s = stud.find(roll_no)
        if s:
            with st.container(border=True):
                grades = s["grades"]
                avg = sum(grades.values()) / len(grades) if grades else 0
                c1, c2, c3 = st.columns(3)
                c1.metric("Name", s["name"])
                c2.metric("Roll No", s["roll_no"])
                c3.metric("Average", f"{avg:.1f}")
                st.write(f"**Age:** {s['age']}  \n**Email:** {s['email']}")
                if grades:
                    st.write("**Grades**")
                    st.dataframe(
                        pd.DataFrame(list(grades.items()), columns=["Subject", "Marks"]),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("No grades recorded yet.")
        else:
            st.error("Student not found.")

# ----------------------------------------------------------------------------
# Teacher Details
# ----------------------------------------------------------------------------
elif page == "Teacher Details":
    st.subheader("Look Up a Teacher")
    with st.container(border=True):
        emp_id = st.text_input("Enter Employee ID")
        search = st.button("Search", use_container_width=True)

    if search and emp_id:
        t = tech.find(emp_id)
        if t:
            with st.container(border=True):
                c1, c2, c3 = st.columns(3)
                c1.metric("Name", t["name"])
                c2.metric("Emp ID", t["emp_id"])
                c3.metric("Subject", t["subject"])
                st.write(f"**Age:** {t['age']}  \n**Email:** {t['email']}")
        else:
            st.error("Teacher not found.")