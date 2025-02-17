import chromadb
import smtplib
import datetime
import openai
from openai import OpenAI  
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialize ChromaDB
db = chromadb.PersistentClient(path="habit_tracker_db")
collection = db.get_or_create_collection("habits")
load_dotenv()
# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to log a habit
# Function to log a habit
def log_habit():
    user_email = input("Enter your email: ").strip().lower()
    habit_type = input("Enter the habit type (e.g., workout, reading, meditation, hydration): ").strip().lower()
    duration = input("Enter duration (in minutes): ").strip()
    intensity = input("Enter intensity (low, medium, high): ").strip().lower()
    mood = input("How did you feel after this habit? (happy, neutral, tired): ").strip().lower()
    timestamp = str(datetime.datetime.now())
    completion_status = input("Did you complete this habit? (yes/no): ").strip().lower()
    reminder_interval = input("Set reminder interval (daily, weekly, custom): ").strip().lower()
    
    # Convert habit data into a text description for ChromaDB
    habit_description = f"User {user_email} logged a {habit_type} habit. Duration: {duration} minutes, Intensity: {intensity}, Mood: {mood}, Completed: {completion_status}, Reminder: {reminder_interval}."

    # Add the habit data to ChromaDB with 'documents' field
    collection.add(
        ids=[timestamp],
        metadatas=[{
            "type": habit_type,
            "timestamp": timestamp,
            "email": user_email,
            "completed": completion_status,
            "duration": duration,
            "intensity": intensity,
            "mood": mood,
            "reminder_interval": reminder_interval
        }],
        documents=[habit_description]  # Required field to avoid error
    )

    print("✅ Habit logged successfully!")

# Function to analyze habit trends
def analyze_habits():
    user_email = input("Enter your email to view habit trends: ").strip().lower()
    habit_category = input("Filter by category (fitness, study, sleep, all): ").strip().lower()
    
    results = collection.query(
        query_texts=[user_email],
        n_results=10  # Get latest 10 habit entries
    )
    
    if not results["documents"]:
        print("❌ No habits found for this email.")
        return
    
    filtered_habits = [doc for doc in results["documents"] if habit_category == "all" or doc["type"] == habit_category]
    
    completed_habits = sum(1 for doc in filtered_habits if doc["completed"] == "yes")
    total_habits = len(filtered_habits)
    success_rate = (completed_habits / total_habits) * 100 if total_habits else 0
    
    print(f"📊 Habit Success Rate: {success_rate:.2f}%")

# Function to send reminder emails
def send_email(recipient, subject, body):
    sender_email = os.getenv("EMAIL_USER") # Replace with an email service API or system
    sender_password = os.getenv("EMAIL_PASSWORD") # Secure method should be used for password storage
    
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_string())
        server.quit()
        print("✅ Reminder sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# Function to send smart reminders
def smart_reminder():
    user_email = input("Enter your email to check for reminders: ").strip().lower()

    # Retrieve habits for the user
    results = collection.query(
        query_texts=[user_email],
        n_results=10  # Adjusts if fewer elements exist
    )

    # Extract habits safely
    if "metadatas" in results and results["metadatas"]:
        for metadata in results["metadatas"][0]:  # First entry in the list
            habit_type = metadata.get("type", "Unknown")
            reminder_interval = metadata.get("reminder_interval", "Unknown")

            print(f"⏰ Reminder: Don't forget your {habit_type} habit! Interval: {reminder_interval}")

    else:
        print("⚠️ No reminders found.")


# AI-Powered Habit Scheduling Suggestions
def adaptive_planning():
    query = input("Ask AI to optimize your schedule (e.g., 'When should I workout?'): ").strip()
    client = OpenAI()  # Create a client instance

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": query}]
    )
    
    print("\n🧠 AI Suggestion:")
    print(response["choices"][0]["message"]["content"])

# Main menu
def main():
    while True:
        print("\n🚀 Habit Tracker Menu:")
        print("1️⃣ Log a Habit")
        print("2️⃣ Analyze Habit Trends")
        print("3️⃣ Smart Reminders (via Email)")
        print("4️⃣ Adaptive Planning (AI Suggestions)")
        print("5️⃣ Exit")
        
        choice = input("Select an option (1-5): ").strip()
        
        if choice == "1":
            log_habit()
        elif choice == "2":
            analyze_habits()
        elif choice == "3":
            smart_reminder()
        elif choice == "4":
            adaptive_planning()
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option, try again.")

if __name__ == "__main__":
    main()
