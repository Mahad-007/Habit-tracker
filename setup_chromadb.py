import chromadb

# Initialize persistent ChromaDB storage
chroma_client = chromadb.PersistentClient(path="./habit_tracker_db")

# Create or load a collection for habit tracking
habit_collection = chroma_client.get_or_create_collection(name="habits")

print("ChromaDB setup complete! Database is ready for use.")


#CHECK WORKING OF DB
habit_collection.add(
    ids=["habit1"],
    documents=["Completed a 30-minute workout"],
    metadatas=[{"category": "fitness", "duration": 30}]
)

# Retrieve the stored habit
results = habit_collection.query(query_texts=["workout"], n_results=1)
print(results)
