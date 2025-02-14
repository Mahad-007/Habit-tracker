import chromadb
import openai
from datetime import datetime, timedelta
import json

# 🔹 Initialize ChromaDB (Persistent Storage)
chroma_client = chromadb.PersistentClient(path="./habit_tracker_db")
habit_collection = chroma_client.get_or_create_collection(name="habits")

# 🔹 OpenAI API for AI Insights (Set your API key)
openai.api_key = "your-api-key"

# Function to get embeddings for AI-based retrieval
def get_embedding(text):
    response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    return response['data'][0]['embedding']

# 🔹 Function to Log a New Habit Entry
def log_habit():
    habit_type = input("Enter habit type (fitness/study/sleep): ").strip().lower()
    description = input("Describe your habit: ").strip()
    timestamp = datetime.now().isoformat()

    habit_id = f"habit-{int(datetime.now().timestamp())}"

    # Add entry to ChromaDB
    habit_collection.add(
        ids=[habit_id],
        documents=[description],
        metadatas=[{
            "type": habit_type,
            "timestamp": timestamp
        }],
        embeddings=[get_embedding(description)]  # Store embeddings for AI-based retrieval
    )

    print("\n✅ Habit logged successfully!")

# 🔹 Function to Retrieve Past Habits
def retrieve_habits():
    query = input("Search your past habits: ").strip()
    
    results = habit_collection.query(
        query_texts=[query],
        n_results=3
    )

    if results["documents"]:
        print("\n📌 Past Habit Logs:")
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            print(f"🔹 {doc} | Date: {meta['timestamp']}")
    else:
        print("\n❌ No matching habits found.")

# 🔹 AI-Powered Smart Reminders
def smart_reminder():
    reminder_type = input("What reminder do you need? (fitness/study/sleep): ").strip().lower()

    # Query past data for insights
    results = habit_collection.query(
        query_texts=[f"past {reminder_type} habits"],
        n_results=5
    )

    if results["documents"]:
        latest_entry = results["metadatas"][0][0]
        last_logged_date = datetime.fromisoformat(latest_entry["timestamp"])

        # AI-Generated Reminder Logic
        if datetime.now() - last_logged_date > timedelta(days=2):
            print(f"\n🚀 You haven't logged a {reminder_type} habit in 2+ days. Time to get back on track!")
        else:
            print(f"\n✅ Great job! You last logged this habit on {latest_entry['timestamp']}. Keep it up!")
    else:
        print("\n❌ No data found for this habit. Start logging now!")

# 🔹 Performance Tracking & Insights
def analyze_performance():
    habit_type = input("Analyze which habit? (fitness/study/sleep): ").strip().lower()

    results = habit_collection.query(
        query_texts=[f"past {habit_type} habits"],
        n_results=10
    )

    if results["documents"]:
        total_entries = len(results["documents"][0])
        print(f"\n📊 You've logged {total_entries} {habit_type} habits recently.")

        # Generate AI insights
        ai_input = f"Analyze my past {habit_type} habits and provide improvement suggestions."
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": ai_input}]
        )

        print("\n🔍 AI Analysis & Suggestions:")
        print(response["choices"][0]["message"]["content"])
    else:
        print("\n❌ No habit data found.")

# 🔹 Adaptive Planning: AI-Driven Habit Optimization
def adaptive_planning():
    query = input("Ask AI to optimize your schedule (e.g., 'When should I workout?'): ").strip()

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": query}]
    )

    print("\n🧠 AI Suggestion:")
    print(response["choices"][0]["message"]["content"])

# 🔹 Main Menu
def main():
    while True:
        print("\n📅 Habit Tracker - Main Menu")
        print("1️⃣ Log a Habit")
        print("2️⃣ Retrieve Past Habits")
        print("3️⃣ Smart Reminders")
        print("4️⃣ Analyze Performance")
        print("5️⃣ Adaptive Planning (AI Suggestions)")
        print("6️⃣ Exit")

        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == "1":
            log_habit()
        elif choice == "2":
            retrieve_habits()
        elif choice == "3":
            smart_reminder()
        elif choice == "4":
            analyze_performance()
        elif choice == "5":
            adaptive_planning()
        elif choice == "6":
            print("\n👋 Exiting Habit Tracker. Stay disciplined!")
            break
        else:
            print("\n❌ Invalid choice. Please select a valid option.")

# Run the Habit Tracker
if __name__ == "__main__":
    main()
