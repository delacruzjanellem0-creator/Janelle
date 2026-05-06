import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

# ---------------- DATABASE ----------------
conn = sqlite3.connect("students.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS students (
    name TEXT,
    quiz REAL,
    exam REAL,
    project REAL,
    final REAL,
    date TEXT
)
""")
conn.commit()


# ---------------- FUNCTIONS ----------------
def add_student(
        name, quiz, exam, project):
    final = (quiz * 0.3) + (exam * 0.4) + (project * 0.3)
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)",
              (name, quiz, exam, project, final, date))
    conn.commit()
    return final


def get_data():
    return pd.read_sql("SELECT * FROM students", conn)


# DELETE FUNCTION
def delete_student(name, quiz, exam, project, final, date):
    c.execute("""
        DELETE FROM students 
        WHERE name=? AND quiz=? AND exam=? AND project=? AND final=? AND date=?
    """, (name, quiz, exam, project, final, date))
    conn.commit()


# ---------------- UI ----------------
st.title("Student Management & Grade Analytics System")

menu = st.sidebar.selectbox("Menu", ["Add Student", "View Records", "Analytics"])

# ---------------- ADD STUDENT ----------------
if menu == "Add Student":
    st.subheader("Add Student Record")

    name = st.text_input("Student Name")
    quiz = st.slider("Quiz Score", 0, 100)
    exam = st.slider("Exam Score", 0, 100)
    project = st.slider("Project Score", 0, 100)

    if st.button("Save Record"):
        final = add_student(name, quiz, exam, project)
        st.success(f"Saved! Final Grade: {final:.2f}")

# ---------------- VIEW RECORDS ----------------
elif menu == "View Records":
    st.subheader("Student Records")

    df = get_data()

    if not df.empty:
        # Add Status & Remarks columns
        df["Status"] = df["final"].apply(lambda x: "✔" if x >= 75 else "✘")
        df["Remarks"] = df["final"].apply(lambda x: "Passed" if x >= 75 else "Failed")

        # Make table FULL WIDTH
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.subheader("Remove Student")

        # Dropdown to select student to delete
        selected_index = st.selectbox(
            "Select a record to remove",
            df.index,
            format_func=lambda i: f"{df.loc[i, 'name']} | {df.loc[i, 'date']}"
        )

        if st.button("Delete Selected Record"):
            row = df.loc[selected_index]

            delete_student(
                row['name'],
                row['quiz'],
                row['exam'],
                row['project'],
                row['final'],
                row['date']
            )

            st.warning(f"{row['name']} removed!")
            st.rerun()

    else:
        st.info("No records available.")


# ---------------- ANALYTICS ----------------
elif menu == "Analytics":
    st.subheader("Performance Analytics")

    df = get_data()

    if not df.empty:
        st.write("Average Scores:")
        st.write(df[['quiz', 'exam', 'project', 'final']].mean())

        # Chart
        fig, ax = plt.subplots()
        df[['quiz', 'exam', 'project']].mean().plot(kind='bar', ax=ax)
        ax.set_title("Average Scores")
        st.pyplot(fig)
    else:
        st.warning("No data available.")