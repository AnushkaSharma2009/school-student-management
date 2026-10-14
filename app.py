
import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="School Student Management", page_icon="🎓")

def connect():
    return sqlite3.connect("students.db")

def setup():
    con = connect()
    con.execute("""
        CREATE TABLE IF NOT EXISTS students(
            roll INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            student_class TEXT,
            age INTEGER,
            email TEXT
        )
    """)
    con.commit()
    con.close()

def get_students():
    con = connect()
    df = pd.read_sql_query("SELECT * FROM students ORDER BY roll", con)
    con.close()
    return df

setup()

st.title("🎓 School Student Management System")
st.write("Welcome to our School Student Portal!")
st.caption("A Class 12 Computer Science Project")

menu = st.sidebar.selectbox(
    "Choose an option",
    ["Home", "Add Student", "View Students",
     "Search Student", "Update Student", "Delete Student"]
)

if menu == "Home":
    df = get_students()
    st.header("Home")
    st.write("Manage school student records easily.")
    st.metric("Total Students", len(df))
    st.info("Use the menu on the left to manage records.")

elif menu == "Add Student":
    st.header("Add New Student")
    with st.form("add"):
        roll = st.number_input("Roll Number", min_value=1, step=1)
        name = st.text_input("Student Name")
        cls = st.selectbox("Class", ["11", "12"])
        age = st.number_input("Age", 15, 20, 17)
        email = st.text_input("Email")
        submit = st.form_submit_button("Add Student")

    if submit:
        if not name.strip():
            st.warning("Enter the student's name.")
        else:
            try:
                con = connect()
                con.execute(
                    "INSERT INTO students VALUES(?,?,?,?,?)",
                    (roll, name.strip(), cls, age, email)
                )
                con.commit()
                con.close()
                st.success("Student added successfully!")
            except sqlite3.IntegrityError:
                st.error("This roll number already exists.")

elif menu == "View Students":
    st.header("All Student Records")
    df = get_students()
    if df.empty:
        st.info("No student records yet. Add a student first.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "Search Student":
    st.header("Search Student")
    roll = st.number_input("Enter Roll Number", min_value=1, step=1)
    if st.button("Search"):
        con = connect()
        result = con.execute(
            "SELECT * FROM students WHERE roll=?", (roll,)
        ).fetchone()
        con.close()
        if result:
            st.success("Student found!")
            st.write("Roll Number:", result[0])
            st.write("Name:", result[1])
            st.write("Class:", result[2])
            st.write("Age:", result[3])
            st.write("Email:", result[4])
        else:
            st.warning("Student not found.")

elif menu == "Update Student":
    st.header("Update Student Details")
    df = get_students()
    if df.empty:
        st.info("Add a student first.")
    else:
        roll = st.selectbox("Select Roll Number", df["roll"].tolist())
        student = df[df["roll"] == roll].iloc[0]
        with st.form("update"):
            name = st.text_input("Name", value=student["name"])
            cls = st.selectbox(
                "Class", ["11", "12"],
                index=["11", "12"].index(str(student["student_class"]))
            )
            age = st.number_input(
                "Age", 15, 20, int(student["age"])
            )
            email = st.text_input("Email", value=student["email"] or "")
            save = st.form_submit_button("Save Changes")
        if save:
            if not name.strip():
                st.warning("Name is required.")
            else:
                con = connect()
                con.execute(
                    """UPDATE students SET name=?, student_class=?,
                    age=?, email=? WHERE roll=?""",
                    (name.strip(), cls, age, email, roll)
                )
                con.commit()
                con.close()
                st.success("Student updated!")
                st.rerun()

elif menu == "Delete Student":
    st.header("Delete Student Record")
    df = get_students()
    if df.empty:
        st.info("No records to delete.")
    else:
        roll = st.selectbox("Select Roll Number", df["roll"].tolist())
        st.write("Student:", df[df["roll"] == roll].iloc[0]["name"])
        confirm = st.checkbox("Confirm deletion")
        if st.button("Delete Student"):
            if confirm:
                con = connect()
                con.execute("DELETE FROM students WHERE roll=?", (roll,))
                con.commit()
                con.close()
                st.success("Student deleted!")
                st.rerun()
            else:
                st.warning("Please confirm deletion.")
