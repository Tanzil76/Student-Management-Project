import json
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd
import streamlit as st

# Persistence

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



# Domain classes (same logic as the original script, adapted for Streamlit
# forms instead of blocking input() calls)

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


# Page config & styling

st.set_page_config(page_title="School Manager", page_icon="🎓", layout="wide")

st.markdown(
    """
    <style>
        .main { background-color: #f7f8fb; }
        div.block-container { padding-top: 2rem; }
        .app-title {
            font-size: 2.1rem;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 0;
        }
        .app-subtitle {
            color: #6b7280;
            margin-top: 0.1rem;
            margin-bottom: 1.5rem;
        }
        .metric-card {
            background: white;
            border-radius: 14px;
            padding: 1.1rem 1.3rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid #eef0f3;
        }
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
        }
        section[data-testid="stSidebar"] {
            background-color: #111827;
        }
        section[data-testid="stSidebar"] * {
            color: #f3f4f6 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# Sidebar navigation

with st.sidebar:
    st.markdown("## 🎓 School Manager")
    st.caption("Students • Teachers • Grades")
    page = st.radio(
        "Navigate",
        [
            "📊 Dashboard",
            "📝 Register Student",
            "👨‍🏫 Register Teacher",
            "✏️ Add Grade",
            "🔍 Student Details",
            "🔎 Teacher Details",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption(f"Data file: `{DATABASE}`")

st.markdown('<p class="app-title">School Management System</p>', unsafe_allow_html=True)
st.markdown('<p class="app-subtitle">A simple, friendly dashboard for managing students, teachers and grades.</p>', unsafe_allow_html=True)


# Dashboard

if page == "📊 Dashboard":
    col1, col2, col3 = st.columns(3)
    total_students = len(data["students"])
    total_teachers = len(data["teachers"])
    all_grades = [m for s in data["students"] for m in s["grades"].values()]
    avg_grade = sum(all_grades) / len(all_grades) if all_grades else 0

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("👨‍🎓 Total Students", total_students)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("👨‍🏫 Total Teachers", total_teachers)
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📈 Average Grade", f"{avg_grade:.1f}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
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


# Register Student

elif page == "📝 Register Student":
    st.subheader("Register a new student")
    with st.form("register_student_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full name")
            age = st.number_input("Age", min_value=3, max_value=100, step=1)
        with c2:
            email = st.text_input("Email")
            roll_no = st.text_input("Roll number")
        submitted = st.form_submit_button("Register Student", use_container_width=True)

    if submitted:
        if not name or not roll_no or not email:
            st.error("Please fill in all fields.")
        else:
            ok, msg = stud.register(name, int(age), email, roll_no)
            st.success(msg) if ok else st.error(msg)


# Register Teacher

elif page == "👨‍🏫 Register Teacher":
    st.subheader("Register a new teacher")
    with st.form("register_teacher_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full name")
            age = st.number_input("Age", min_value=18, max_value=100, step=1)
            subject = st.text_input("Subject taught")
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


# Add Grade

elif page == "✏️ Add Grade":
    st.subheader("Add a grade for a student")
    if not data["students"]:
        st.info("No students registered yet. Register a student first.")
    else:
        roll_options = {f"{s['name']} ({s['roll_no']})": s["roll_no"] for s in data["students"]}
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


# Student Details

elif page == "🔍 Student Details":
    st.subheader("Look up a student")
    roll_no = st.text_input("Enter roll number")
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


# Teacher Details

elif page == "🔎 Teacher Details":
    st.subheader("Look up a teacher")
    emp_id = st.text_input("Enter employee ID")
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