import chromadb
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialize ChromaDB
db = chromadb.PersistentClient(path="habit_tracker_db")
collection = db.get_or_create_collection("habits")

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
        }]
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
    sender_email = "your-email@gmail.com"  # Replace with an email service API or system
    sender_password = "your-app-password"  # Secure method should be used for password storage
    
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
    results = collection.query(
        query_texts=[user_email],
        n_results=10
    )
    
    if not results["documents"]:
        print("❌ No habit data found.")
        return
    
    for doc in results["documents"]:
        habit_type = doc["type"]
        completed = doc["completed"]
        timestamp = datetime.datetime.strptime(doc["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
        reminder_interval = doc.get("reminder_interval", "daily")
        
        days_since_last = (datetime.datetime.now() - timestamp).days
        if completed == "no" and ((reminder_interval == "daily" and days_since_last >= 1) or 
                                   (reminder_interval == "weekly" and days_since_last >= 7)):
            reminder_msg = f"Hey! You haven't completed your {habit_type} habit. Stay consistent! 💪"
            send_email(user_email, "Habit Reminder", reminder_msg)

# Main menu
def main():
    while True:
        print("\n🚀 Habit Tracker Menu:")
        print("1️⃣ Log a Habit")
        print("2️⃣ Analyze Habit Trends")
        print("3️⃣ Smart Reminders (via Email)")
        print("4️⃣ Exit")
        
        choice = input("Select an option (1-4): ").strip()
        
        if choice == "1":
            log_habit()
        elif choice == "2":
            analyze_habits()
        elif choice == "3":
            smart_reminder()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option, try again.")

if __name__ == "__main__":
    main()
