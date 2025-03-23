import re

def parse_invoice_command(text):
    try:
        # Improved pattern to handle multiple products with exact splitting
        match = re.match(
            r'^/generate\s+invoice\s+for\s+(.+?)\s*:\s*(.+)$', 
            text, 
            re.IGNORECASE
        )
        
        if not match:
            return {"customer": None, "products": []}

        customer_part, products_part = match.groups()
        
        # Clean customer name
        customer = re.sub(r'\s+', ' ', customer_part.strip()).title()
        
        # Split products while preserving multi-word names
        products = []
        for item in re.split(r',\s*(?=\d+\s)', products_part):
            item = item.strip()
            if not item:
                continue
                
            # Match quantity and product (including numbers and spaces)
            product_match = re.fullmatch(r'\s*(\d+)\s+(.+)\s*', item)
            if product_match:
                qty, product = product_match.groups()
                products.append((product.strip(), int(qty)))
        
        return {
            "customer": customer,
            "products": products
        }

    except Exception as e:
        print(f"Parsing error: {str(e)}")
        return {"customer": None, "products": []}