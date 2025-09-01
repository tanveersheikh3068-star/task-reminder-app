import streamlit as st
import pandas as pd
from datetime import datetime, time, date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ------------------ Email Sender Function ------------------
def send_email(subject, body, to_email):
    # Ethereal Email Details (FREE)
    ethereal_address = st.secrets["EMAIL_ADDRESS"]
    ethereal_password = st.secrets["EMAIL_PASSWORD"]

    msg = MIMEMultipart()
    msg['From'] = ethereal_address
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.ethereal.email', 587)
        server.starttls()
        server.login(ethereal_address, ethereal_password)
        text = msg.as_string()
        server.sendmail(ethereal_address, to_email, text)
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
    
    # Date and Time input alag-alag
    task_date = st.date_input("Kab remind karna hai? (Date select karen):", min_value=date.today())
    task_time = st.time_input("Time select karen:", value=time(9, 0))
    
    # Combine date and time
    task_datetime = datetime.combine(task_date, task_time)
    
    submitted = st.form_submit_button("Add Task ✅")

    if submitted:
        if task_name:
            new_task = {
                "Task Name": task_name,
                "Description": task_desc,
                "Time": task_datetime,
                "Created At": datetime.now(),
                "Notified": False
            }

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

# ------------------ Display Pending Tasks ------------------
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

# ------------------ Manual Check for Notifications ------------------
if st.button("Check for Notifications Now 🔍"):
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
                    df.at[index, 'Notified'] = True
                    st.write(f"Notification sent for: {row['Task Name']}")

            df.to_csv("tasks.csv", index=False)
            st.rerun()
        else:
            st.info("No tasks to notify.")
    except FileNotFoundError:
        st.info("No task file found.")
