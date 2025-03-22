import re
import os
import requests
from dotenv import load_dotenv
from mongo_queries import get_customer_by_name, get_product_by_name
from invoice_generator import create_invoice

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def process_telegram_update(update):
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "").strip()

    if text.startswith("/start"):
        send_message(chat_id, "Welcome! Use:\n/generate invoice for <customer> for <quantity> <product>")
        return

    if text.startswith("/generate"):
        try:
            # Improved regex pattern with better capture groups
            pattern = re.compile(
                r"/generate invoice for (.+?) for (\d+) (.+)$",
                re.IGNORECASE
            )
            match = pattern.fullmatch(text)
            
            if not match:
                send_message(chat_id, "Invalid format. Use:\n/generate invoice for <customer> for <quantity> <product>")
                return

            customer_name = match.group(1).strip()
            quantity_str = match.group(2).strip()
            product_name = match.group(3).strip()

            print(f"\n📩 Received command:")
            print(f"Customer: '{customer_name}'")
            print(f"Quantity: '{quantity_str}'")
            print(f"Product: '{product_name}'")

            # Validate quantity
            if not quantity_str.isdigit():
                send_message(chat_id, "❌ Invalid quantity format. Please enter a number.")
                return

            quantity = int(quantity_str)

            # Fetch data from MongoDB with debug logging
            print("\n🔍 Starting database lookups...")
            customer = get_customer_by_name(customer_name)
            product = get_product_by_name(product_name)

            print(f"\n📦 Database results:")
            print(f"Customer found: {bool(customer)}")
            print(f"Product found: {bool(product)}")

            if not customer:
                send_message(chat_id, f"❌ Customer '{customer_name}' not found in database")
                return

            if not product:
                send_message(chat_id, f"❌ Product '{product_name}' not found in database")
                return

            # Generate Invoice
            try:
                unit_price = product["unit_price"]
                subtotal = unit_price * quantity
                tax_rate = float(os.getenv("TAX_RATE", 18))
                tax = (subtotal * tax_rate) / 100
                total = subtotal + tax

                pdf_filename = f"invoices/{customer_name}_invoice.pdf"
                products_list = [{
                    "name": product["name"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "subtotal": subtotal
                }]

                create_invoice(customer, products_list, total, tax, pdf_filename)
                send_pdf(chat_id, pdf_filename)
                print(f"\n✅ Invoice generated successfully: {pdf_filename}")

            except Exception as e:
                print(f"❌ Invoice generation error: {str(e)}")
                send_message(chat_id, f"⚠️ Error generating invoice: {str(e)}")

        except Exception as e:
            print(f"❌ Main error: {str(e)}")
            send_message(chat_id, f"⚠️ System error: {str(e)}")

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