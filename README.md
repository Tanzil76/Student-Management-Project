# 🎓 School Management System

A simple, clean **School Management System** built with **Python** and **Streamlit**, demonstrating solid object-oriented design combined with an interactive web UI. Manage students, teachers, and grades — all backed by lightweight JSON storage, no database required.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- 📝 **Register Students** — name, age, email, roll number, with email validation and duplicate checks
- 👨‍🏫 **Register Teachers** — name, age, email, subject, employee ID
- 📊 **Grade Management** — add grades per subject and auto-calculate averages
- 🔍 **Lookup** — search students by roll number or teachers by employee ID
- 📈 **Dashboard** — live metrics (total students, teachers, average grade) and data tables
- 💾 **Persistent Storage** — all data saved to a local `school_data.json` file
- 🎨 **Polished UI** — custom-styled Streamlit interface with cards, gradients, and a sidebar navigation

## 🏗️ Project Structure

The project follows clean object-oriented principles:

- `Persons` — an abstract base class defining the shared interface (`get_role`) and a static `validate_email` helper
- `Student` — handles registration, grade tracking, and lookups for students
- `Teacher` — handles registration and lookups for teachers

This design makes it easy to extend the system (e.g., add an `Admin` class or a `Course` entity) without touching existing code.

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
git clone https://github.com/<your-username>/school-management-system.git
cd school-management-system
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## 📦 Requirements

```
streamlit
pandas
```

## 🖼️ Screenshots

_Add a few screenshots of the Dashboard, Register Student, and Student Details pages here._

## 🗺️ Roadmap

- [ ] Edit/delete existing student or teacher records
- [ ] Export data to CSV/Excel
- [ ] Role-based login (admin vs. viewer)
- [ ] Grade trend charts over time
- [ ] Switch storage to SQLite for larger datasets

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to open a PR or an issue.

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
<img width="958" height="415" alt="image" src="https://github.com/user-attachments/assets/c9baebd2-fc3b-45bd-aaa2-7582c7e39a26" />
