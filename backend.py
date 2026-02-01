import mysql.connector
import pandas as pd
from fpdf import FPDF
import datetime

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="billing_inventory"
    )

# ---------- ADD PRODUCT ----------
def add_product(name, category, price, stock):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Products_Simple (product_name, category, price, stock)
        VALUES (%s, %s, %s, %s)
        """,
        (name, category, price, stock)
    )
    conn.commit()
    cursor.close()
    conn.close()

# ---------- FETCH PRODUCTS ----------
def get_all_products():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM Products_Simple", conn)
    conn.close()
    return df

# ---------- UPDATE PRODUCT ----------
def update_product(product_id, name, category, price, stock):
    conn = get_connection()
    cursor = conn.cursor()

    updates = []
    values = []

    if name.strip():
        updates.append("product_name=%s")
        values.append(name)

    if category.strip():
        updates.append("category=%s")
        values.append(category)

    if price > 0:
        updates.append("price=%s")
        values.append(price)

    if stock > 0:
        updates.append("stock=%s")
        values.append(stock)

    if not updates:
        cursor.close()
        conn.close()
        return False

    values.append(product_id)
    sql = f"""
        UPDATE Products_Simple
        SET {', '.join(updates)}
        WHERE product_id=%s
    """
    cursor.execute(sql, tuple(values))
    conn.commit()

    cursor.close()
    conn.close()
    return True

# ---------- DELETE PRODUCT ----------
def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM Products_Simple WHERE product_id=%s",
        (product_id,)
    )
    conn.commit()
    deleted = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return deleted

# ---------- STOCK REPORT ----------
def stock_report():
    df = get_all_products()
    in_stock = df[df["stock"] > 5]
    low_stock = df[df["stock"] <= 5]
    return df, in_stock, low_stock


from fpdf import FPDF
import datetime

def generate_stock_report_pdf(df, filename="stock_report.pdf"):
    in_stock = df[df["stock"] > 5]
    low_stock = df[df["stock"] <= 5]

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Inventory Stock Report", ln=True, align="C")
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(5)

    # ---------- In Stock Products ----------
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "In Stock Products", ln=True)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(30, 10, "ID", 1)
    pdf.cell(60, 10, "Product Name", 1)
    pdf.cell(40, 10, "Category", 1)
    pdf.cell(30, 10, "Stock", 1)
    pdf.cell(30, 10, "Price", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 12)
    for _, row in in_stock.iterrows():
        pdf.cell(30, 10, str(row["product_id"]), 1)
        pdf.cell(60, 10, row["product_name"], 1)
        pdf.cell(40, 10, row["category"], 1)
        pdf.cell(30, 10, str(row["stock"]), 1)
        pdf.cell(30, 10, str(row["price"]), 1)
        pdf.ln()

    pdf.ln(5)

    # ---------- Low Stock Products ----------
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Low Stock Products (<=5)", ln=True)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(30, 10, "ID", 1)
    pdf.cell(60, 10, "Product Name", 1)
    pdf.cell(40, 10, "Category", 1)
    pdf.cell(30, 10, "Stock", 1)
    pdf.cell(30, 10, "Price", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 12)
    for _, row in low_stock.iterrows():
        pdf.cell(30, 10, str(row["product_id"]), 1)
        pdf.cell(60, 10, row["product_name"], 1)
        pdf.cell(40, 10, row["category"], 1)
        pdf.cell(30, 10, str(row["stock"]), 1)
        pdf.cell(30, 10, str(row["price"]), 1)
        pdf.ln()

    pdf.output(filename)
    return filename
