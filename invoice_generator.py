from fpdf import FPDF
from datetime import datetime

def create_invoice(customer, products, total, tax, pdf_filename):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Invoice", align="C", ln=True)

    # Customer Info
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Customer: {customer['name']}", ln=True)
    pdf.cell(0, 10, f"Phone: {customer['phone']}", ln=True)
    pdf.cell(0, 10, f"Address: {customer['address']}", ln=True)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

    # Table Header
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(60, 10, "Product", border=1)
    pdf.cell(40, 10, "Quantity", border=1)
    pdf.cell(40, 10, "Unit Price", border=1)
    pdf.cell(40, 10, "Subtotal", border=1)
    pdf.ln()

    # Table Content
    for product in products:
        pdf.set_font("Arial", size=12)
        pdf.cell(60, 10, product['name'], border=1)
        pdf.cell(40, 10, str(product['quantity']), border=1)
        pdf.cell(40, 10, f"{product['unit_price']:.2f}", border=1)
        pdf.cell(40, 10, f"{product['subtotal']:.2f}", border=1)
        pdf.ln()

    # Total
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Tax: {tax:.2f}", ln=True)
    pdf.cell(0, 10, f"Total: {total:.2f}", ln=True)

    # Save PDF
    pdf.output(pdf_filename)
