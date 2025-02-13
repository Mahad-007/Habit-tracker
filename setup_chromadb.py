import chromadb

# Initialize persistent ChromaDB storage
chroma_client = chromadb.PersistentClient(path="./habit_tracker_db")

# Create or load a collection for habit tracking
habit_collection = chroma_client.get_or_create_collection(name="habits")

print("ChromaDB setup complete! Database is ready for use.")




