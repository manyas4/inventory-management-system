import streamlit as st
from backend import (
    add_product,
    get_all_products,
    update_product,
    delete_product,
    stock_report
)

st.set_page_config(page_title="Inventory System", layout="wide")
st.title("📦 Inventory Management System")

menu = st.sidebar.radio(
    "Menu",
    ["Add Product", "View Inventory", "Update Product", "Delete Product", "Stock Report"]
)

# ---------------- ADD PRODUCT ----------------
if menu == "Add Product":
    st.subheader("Add New Product")

    name = st.text_input("Product Name")
    category = st.text_input("Category")
    price = st.number_input("Price", min_value=0.0)
    stock = st.number_input("Stock", min_value=0, step=1)

    if st.button("Add Product"):
        if name:
            add_product(name, category, price, stock)
            st.success("Product added successfully ✅")
        else:
            st.error("Product name is required")

# ---------------- VIEW INVENTORY ----------------
elif menu == "View Inventory":
    st.subheader("Inventory List")
    df = get_all_products()
    st.dataframe(df, use_container_width=True)

# ---------------- UPDATE PRODUCT ----------------
elif menu == "Update Product":
    st.subheader("Update Product")

    df = get_all_products()

    if df.empty:
        st.warning("No products available")
    else:
        product_map = {
            f"{row.product_name} (ID:{row.product_id})": row.product_id
            for _, row in df.iterrows()
        }

        selected = st.selectbox("Select Product to Update", product_map.keys())
        product_id = product_map[selected]

        new_name = st.text_input("New Name (leave blank to keep current)")
        new_category = st.text_input("New Category (leave blank to keep current)")
        new_price = st.number_input("New Price (0 = keep current)", min_value=0.0)
        new_stock = st.number_input("New Stock (0 = keep current)", min_value=0)

        if st.button("Update Product"):
            updated = update_product(
                product_id,
                new_name,
                new_category,
                new_price,
                new_stock
            )
            if updated:
                st.success("Product updated successfully ✅")
                
            else:
                st.info("No changes made")

# ---------------- DELETE PRODUCT ----------------
elif menu == "Delete Product":
    st.subheader("Delete Product")

    df = get_all_products()

    if df.empty:
        st.warning("No products available")
    else:
        product_map = {
            f"{row.product_name} (ID:{row.product_id})": row.product_id
            for _, row in df.iterrows()
        }

        selected = st.selectbox("Select Product to Delete", product_map.keys())
        product_id = product_map[selected]

        if st.button("Delete Product"):
            if delete_product(product_id):
                st.success("Product deleted successfully 🗑️")
                
            else:
                st.error("Product not found")

# ---------------- STOCK REPORT ----------------
elif menu == "Stock Report":
    st.subheader("Stock Report")

    df, in_stock, low_stock = stock_report()

    st.markdown("### 📦 In Stock Products")
    st.dataframe(in_stock, use_container_width=True)

    st.markdown("### ⚠️ Low Stock Products (≤ 5)")
    st.dataframe(low_stock, use_container_width=True)

    # ---------- Download PDF ----------
    if st.button("Download Stock Report as PDF"):
        from backend import generate_stock_report_pdf
        pdf_file = generate_stock_report_pdf(df)
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="Download PDF",
                data=f,
                file_name="Stock_Report.pdf",
                mime="application/pdf"
            )
