from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables from .env file
load_dotenv()

# Build the connection URI using environment variables
URI = f"mongodb+srv://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@xplore.1v68hbs.mongodb.net/?retryWrites=true&w=majority&appName=xplore"

# Create an AsyncMongoClient instance
client = AsyncMongoClient(URI, server_api=ServerApi("1"))

# Select the database and collections
db = client[os.getenv("DB_NAME")]
owner = db["owner"]
warung = db["warung"]

# Define the asynchronous function to test the connection
async def coba():
    try:
        print("Memulai koneksi...")
        
        # Check if the connection is successful by listing database names
        await client.admin.command('ping')
        print("Koneksi berhasil!")

        # Fetch a document from the 'owner' collection
        print("Mencari dokumen...")
        document = await owner.find_one({"phone_number": "+6281384985141"})
        
        if document:
            state = document.get("state")
            print("State:", state)
        else:
            print("Dokumen tidak ditemukan.")
            
    except Exception as e:
        print("Terjadi kesalahan:", e)
    finally:
        # Close the connection
        await client.close()
        print("Koneksi ditutup.")

# Run the asynchronous function using asyncio.run()
if __name__ == "__main__":
    asyncio.run(coba())