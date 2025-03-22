from dotenv import load_dotenv
import os
import re
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['Invoice_Generator']

# Collections
customers = db['customer_data']
products = db['product_data']

def get_customer_by_name(original_name):
    try:
        # Normalize whitespace and special characters
        search_name = re.sub(r'\s+', ' ', original_name.strip())
        print(f"\n🔍 Customer search for: '{original_name}' (normalized: '{search_name}')")

        # Create flexible search pattern
        pattern = re.compile(r'^\s*' + re.escape(search_name) + r'\s*$', re.IGNORECASE)
        
        # Search with case insensitivity and flexible whitespace
        customer = customers.find_one({
            "Name": pattern
        })

        if customer:
            print(f"✅ Found customer: {customer['Name']}")
            # Handle phone number format
            phone_data = customer.get("Number", {})
            phone = str(phone_data.get("$numberLong", "")) if isinstance(phone_data, dict) else str(phone_data)
            
            return {
                "name": customer["Name"],  # Preserve original case from DB
                "phone": phone,
                "address": customer.get("Address")
            }
        
        # Debug: Check first 3 customer names
        print("🔎 Sample customers in DB:")
        for doc in customers.find().limit(3):
            print(f"- {doc.get('Name')}")
        
        return None

    except Exception as e:
        print(f"❌ Customer search error: {str(e)}")
        return None

def get_product_by_name(original_name):
    try:
        # Normalize whitespace and special characters
        search_name = re.sub(r'\s+', ' ', original_name.strip())
        print(f"\n🔍 Product search for: '{original_name}' (normalized: '{search_name}')")

        # Create flexible search pattern
        pattern = re.compile(r'^\s*' + re.escape(search_name) + r'\s*$', re.IGNORECASE)
        
        # Search with case insensitivity and flexible whitespace
        product = products.find_one({
            "name": pattern
        })

        if product:
            print(f"✅ Found product: {product['name']}")
            return {
                "name": product["name"],  # Preserve original case from DB
                "unit_price": product.get("unit_price"),
                "mrp": product.get("mrp"),
                "description": product.get("description"),
                "seller": product.get("seller")
            }
        
        # Debug: Check first 3 product names
        print("🔎 Sample products in DB:")
        for doc in products.find().limit(3):
            print(f"- {doc.get('name')}")
        
        return None

    except Exception as e:
        print(f"❌ Product search error: {str(e)}")
        return None