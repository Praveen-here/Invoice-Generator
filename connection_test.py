from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client['Invoice_Generator']

# Fetch and display customer data
print("Connected to MongoDB")

customers = db['customer_data']

# Display all customers
print("\n--- All Customers ---")
for customer in customers.find():
    print(customer)
