import streamlit as st
import pandas as pd
from datetime import datetime, time, date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ------------------ Email Sender Function (GMAIL) ------------------
def send_email(subject, body, to_email):
    # Gmail Details from Secrets
    gmail_address = st.secrets["GMAIL_ADDRESS"]
    gmail_app_password = st.secrets["GMAIL_PASSWORD"]  # Your App Password

    msg = MIMEMultipart()
    msg['From'] = gmail_address
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_address, gmail_app_password)
        text = msg.as_string()
        server.sendmail(gmail_address, to_email, text)
        server.quit()
        st.success("✅ Notification sent successfully! Check your email.")
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
    
    # Manual Date Input
    date_input_str = st.text_input("Date (YYYY-MM-DD) likhen:", value=date.today().strftime("%Y-%m-%d"))
    # Manual Time Input
    time_input_str = st.text_input("Time (HH:MM) likhen, 24-hour format mein:", value="09:00")
    
    submitted = st.form_submit_button("Add Task ✅")

    if submitted:
        if task_name:
            try:
                # String ko date aur time mein convert karna
                task_date = datetime.strptime(date_input_str, "%Y-%m-%d").date()
                task_time = datetime.strptime(time_input_str, "%H:%M").time()
                # Date aur time ko combine karna
                task_datetime = datetime.combine(task_date, task_time)
                
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
            except ValueError:
                st.error("❌ Galat date ya time format. Sahi format mein likhen (YYYY-MM-DD aur HH:MM).")
        else:
            st.warning("⚠️ Please task ka naam zaroor likhen.")

# ------------------ Display Pending Tasks ------------------
st.header("Pending Tasks")
try:
    df = pd.read_csv("tasks.csv")
    if not df.empty:
        df['Time'] = pd.to_datetime(df['Time'])
        df['Created At'] = pd.to_datetime(df['Created At'])
        st.dataframe(df)
    else:
        st.info("ℹ️ Abhi tak koi task nahi hai.")
except FileNotFoundError:
    st.info("ℹ️ Abhi tak koi task file nahi bani. Pehla task add karen.")

# ------------------ Manual Check for Notifications ------------------
st.header("Check Notifications")
st.write("**Check Karen** button dabayein. Agar kisi task ka time ho gaya hai toh aap ko email bhej di jayegi.")
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
                    st.write(f"📧 Notification sent for: {row['Task Name']}")

            df.to_csv("tasks.csv", index=False)
            st.rerun()
        else:
            st.info("ℹ️ No tasks to notify.")
    except FileNotFoundError:
        st.info("ℹ️ No task file found.")

# ------------------ Footer ------------------
st.markdown("---")
st.write("**Notification aap ki email par jayegi:** yasirali22444422@gmail.com")
st.write("Agar email nahi aati toh 'Check for Notifications Now' button dabayein.")
