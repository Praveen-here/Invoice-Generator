from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
import uvicorn
from telegram_bot import process_telegram_update
from mongo_queries import get_customer_by_name, get_product_by_name
from invoice_generator import create_invoice

# Load environment variables
load_dotenv()

# Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

# FastAPI App
app = FastAPI()
        
# Health Check Route
@app.get("/")
async def root():
    return {"message": "Invoice Bot is running!"}

# Webhook Endpoint for Telegram Bot
@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    background_tasks.add_task(process_telegram_update, data)
    return {"message": "Message received"}

# API Route to Generate PDF Invoice
@app.get("/generate-invoice")
async def generate_invoice(customer_name: str, product_name: str, quantity: int):
    # Fetch customer and product data from MongoDB
    customer = get_customer_by_name(customer_name)
    if not customer:
        return {"error": "Customer not found"}

    product = get_product_by_name(product_name)
    if not product:
        return {"error": "Product not found"}

    # Calculate subtotal and tax
    unit_price = product["unit_price"]
    subtotal = unit_price * quantity

    tax_rate = float(os.getenv("TAX_RATE", 18))
    tax = (subtotal * tax_rate) / 100
    total = subtotal + tax

    # Create PDF Invoice
    pdf_filename = f"invoices/{customer_name}_invoice.pdf"
    products = [{
        "name": product["name"],
        "quantity": quantity,
        "unit_price": unit_price,
        "subtotal": subtotal
    }]

    create_invoice(customer, products, total, tax, pdf_filename)

    return FileResponse(pdf_filename, media_type='application/pdf', filename=f"{customer_name}_invoice.pdf")

# Run the server
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
