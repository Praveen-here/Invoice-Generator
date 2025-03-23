import re
import os
import requests
from dotenv import load_dotenv
from mongo_queries import get_customer_by_name, get_product_by_name
from invoice_generator import create_invoice
from invoice_parser import parse_invoice_command

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# In telegram_bot.py - Updated process_telegram_update function
# telegram_bot.py (updated process_telegram_update)
def process_telegram_update(update):
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "").strip()

    if text.startswith("/start"):
        send_message(chat_id, "Welcome! Use:\n/generate invoice for Customer Name: Quantity Product, ...\nExample:\n/generate invoice for Hrishita Cheema: 4 Augmentin 625 Duo Tablet, 1 Azithral 500 Tablet")
        return

    if text.startswith("/generate"):
        try:
            parsed = parse_invoice_command(text)
            
            if not parsed["customer"] or not parsed["products"]:
                return send_message(chat_id, "❌ Invalid format. Please use:\n/generate invoice for Customer Name: Quantity Product, ...")

            customer_name = parsed["customer"]
            products = parsed["products"]

            # Fetch customer
            print(f"\n🔍 Searching for customer: {customer_name}")
            customer = get_customer_by_name(customer_name)
            if not customer:
                return send_message(chat_id, f"❌ Customer '{customer_name}' not found")

            # Process products
            valid_products = []
            missing_products = []
            
            for product_name, quantity in products:
                print(f"\n🔍 Processing product: '{product_name}' (Quantity: {quantity})")
                product = get_product_by_name(product_name)
                
                if not product:
                    missing_products.append(product_name)
                    continue
                
                valid_products.append({
                    "name": product["name"],
                    "quantity": quantity,
                    "unit_price": product["unit_price"],
                    "subtotal": product["unit_price"] * quantity
                })

            if missing_products:
                return send_message(chat_id, f"❌ Products not found: {', '.join(missing_products)}")

            # Calculate totals
            total_subtotal = sum(p["subtotal"] for p in valid_products)
            tax_rate = float(os.getenv("TAX_RATE", 18))
            tax = total_subtotal * tax_rate / 100
            total = total_subtotal + tax

            # Generate single PDF with all products
            safe_name = re.sub(r'[^a-z0-9]', '_', customer_name.lower())
            pdf_filename = f"invoices/{safe_name}_invoice.pdf"
            create_invoice(customer, valid_products, total, tax, pdf_filename)
            send_pdf(chat_id, pdf_filename)

        except Exception as e:
            send_message(chat_id, f"⚠️ Error: {str(e)}")
            print(f"System Error: {str(e)}")

def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to send message: {str(e)}")

def send_pdf(chat_id, pdf_filename):
    url = f"{BASE_URL}/sendDocument"
    try:
        with open(pdf_filename, "rb") as pdf:
            files = {"document": pdf}
            data = {"chat_id": chat_id}
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            print(f"📤 PDF sent successfully: {pdf_filename}")
    except Exception as e:
        print(f"❌ Failed to send PDF: {str(e)}")