import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# ------------------ Email Sender Function ------------------
def send_email(subject, body, to_email):
    # Aap ka Gmail address aur App Password yahaan aayega
    gmail_address = "yasirali22444422@gmail.com"
    gmail_app_password = st.secrets["GMAIL_PASSWORD"]  # Ye Streamlit ke Secrets se aayega

    # Email banate hain
    msg = MIMEMultipart()
    msg['From'] = gmail_address
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Server se connect karke email bhejna
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_address, gmail_app_password)
        text = msg.as_string()
        server.sendmail(gmail_address, to_email, text)
        server.quit()
        st.success("Notification sent successfully!")
    except Exception as e:
        st.error(f"Error sending email: {e}")

# ------------------ Streamlit App UI ------------------
st.set_page_config(page_title="Yasir's Task Reminder", page_icon="✅")
st.title("✅ Yasir Bhai ka Task Reminder System")
st.write("Asslam-o-Alaikum! Yahaan apne tasks add karen aur time par notification email paen.")

# Task form
with st.form("task_form"):
    task_name = st.text_input("Task Ka Naam (Chota aur clear likhen):")
    task_desc = st.text_area("Task Ki Details (Kya karna hai?):")
    task_time = st.datetime_input("Kab remind karna hai? (Date aur Time select karen):", min_value=datetime.now())
    submitted = st.form_submit_button("Add Task")

    if submitted:
        if task_name and task_desc:
            # Task ko DataFrame mein add karna
            new_task = {
                "Task Name": task_name,
                "Description": task_desc,
                "Time": task_time,
                "Created At": datetime.now(),
                "Notified": False  # Abhi tak notify nahi hua hai
            }

            # CSV file mein save karna
            try:
                df_existing = pd.read_csv("tasks.csv")
            except FileNotFoundError:
                df_existing = pd.DataFrame(columns=["Task Name", "Description", "Time", "Created At", "Notified"])

            df_new = pd.DataFrame([new_task])
            df_updated = pd.concat([df_existing, df_new], ignore_index=True)
            df_updated.to_csv("tasks.csv", index=False)

            st.success(f"Task '{task_name}' successfully added! Aap ko time par email aa jaye gi.")
            st.balloons()
        else:
            st.warning("Please task ka naam zaroor likhen.")

# ------------------ Check Pending Tasks (Scheduler) ------------------
st.header("Pending Tasks")
try:
    df = pd.read_csv("tasks.csv")
    if not df.empty:
        df['Time'] = pd.to_datetime(df['Time'])
        df['Created At'] = pd.to_datetime(df['Created At'])
        st.dataframe(df)
    else:
        st.info("Abhi tak koi task nahi hai.")
except FileNotFoundError:
    st.info("Abhi tak koi task file nahi bani. Pehla task add karen.")

# ------------------ Check for Notifications (Ye background mein chalta rahega) ------------------
if st.button("Check for Notifications Now"):
    try:
        df = pd.read_csv("tasks.csv")
        if not df.empty:
            df['Time'] = pd.to_datetime(df['Time'])
            now = datetime.now()
            for index, row in df.iterrows():
                if now >= row['Time'] and not row['Notified']:
                    subject = f"[Task Reminder] {row['Task Name']}"
                    body = f"""
Asslam-o-Alaikum Yasir Bhai,

Aap ka task: '{row['Task Name']}'
Details: {row['Description']}
Ka time ho gaya hai: {row['Time']}

Kya aap ne ye task complete kar liya hai?

Yasir Bhai ka Task Reminder System.
"""
                    send_email(subject, body, "yasirali22444422@gmail.com")
                    # Notified status ko update karo
                    df.at[index, 'Notified'] = True
                    st.write(f"Notification sent for: {row['Task Name']}")

            # CSV file ko updated status ke saath save karo
            df.to_csv("tasks.csv", index=False)
        else:
            st.info("No tasks to notify.")
    except FileNotFoundError:
        st.info("No task file found.")