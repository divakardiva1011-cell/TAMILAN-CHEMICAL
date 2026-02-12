import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Phenyl Shop", page_icon="🧴", layout="wide")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("phenyl_shop.db", check_same_thread=False)
cur = conn.cursor()



# Create tables
cur.execute("""
CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price INTEGER,
    stock INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS orders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    phone TEXT,
    address TEXT,
    pincode TEXT,
    product TEXT,
    quantity INTEGER,
    total_price INTEGER,
    payment_method TEXT,
    upi_id TEXT


)
""")

conn.commit()

# ---------------- FUNCTIONS ----------------
def add_product(name, price, stock):
    cur.execute("INSERT INTO products(name, price, stock) VALUES(?,?,?)", (name, price, stock))
    conn.commit()

def get_products():
    cur.execute("SELECT * FROM products")
    return cur.fetchall()

def place_order(customer_name, phone, address, pincode, product, quantity, total_price, payment_method, upi_id):
    cur.execute("""INSERT INTO orders(customer_name, phone, address, pincode, product, quantity, total_price, payment_method, upi_id)
                   VALUES(?,?,?,?,?,?,?,?,?)""",
                (customer_name, phone, address, pincode, product, quantity, total_price, payment_method, upi_id))
    conn.commit()

    cur.execute("INSERT INTO orders(customer_name, phone, product, quantity, total_price) VALUES(?,?,?,?,?)",
                (customer_name, phone, product, quantity, total_price))
    conn.commit()

def get_orders():
    cur.execute("SELECT * FROM orders")
    return cur.fetchall()

def update_stock(product_name, quantity):
    cur.execute("UPDATE products SET stock = stock - ? WHERE name = ?", (quantity, product_name))
    conn.commit()

# Insert default products if empty
cur.execute("SELECT COUNT(*) FROM products")
count = cur.fetchone()[0]

if count == 0:
    add_product("Lemon Phenyl", 80, 50)
    add_product("Pine Phenyl", 90, 40)
    add_product("Rose Phenyl", 85, 30)

# ---------------- UI ----------------
st.title("🧴 TAMILAN CHEMICALS")

menu = ["Home", "Customer Order", "Admin Login"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------- HOME PAGE ----------------
if choice == "Home":
    st.subheader("✨ Welcome to TAMILAN CHEMICAL")
    st.write("We provide best phenyl products for home and industrial cleaning.")

    st.markdown("## 🛒 Available Products")

    products = get_products()
    df = pd.DataFrame(products, columns=["ID", "Product Name", "Price (₹)", "Stock (L)"])
    st.dataframe(df, use_container_width=True)

# ---------------- CUSTOMER ORDER ----------------
elif choice == "Customer Order":
    

    st.subheader("📦 Place Your Order")

    name = st.text_input("Customer Name")
    phone = st.text_input("Mobile Number")
    address = st.text_area("Delivery Address")
    pincode = st.text_input("Pincode")
    payment_method = st.selectbox("Payment Method", ["Cash On Delivery", "UPI Payment"])
    upi_id = st.text_input("UPI ID (Only if UPI Payment)")


    products = get_products()
    product_names = [p[1] for p in products]

    selected_product = st.selectbox("Select Product", product_names)

    quantity = st.number_input("Quantity (Liters)", min_value=1, max_value=100)

    # Get price and stock
    selected_data = [p for p in products if p[1] == selected_product][0]
    price = selected_data[2]
    stock = selected_data[3]

    st.info(f"💰 Price per Liter: ₹{price}")
    st.warning(f"📦 Available Stock: {stock} Liters")

    total_price = price * quantity
    st.success(f"✅ Total Price: ₹{total_price}")

    if st.button("Confirm Order"):
        if name == "" or phone == "":
            st.error("❌ Please fill all details")
        elif quantity > stock:
            st.error("❌ Stock not available for this quantity!")
        else:
            place_order(name, phone, address, pincode, selected_product, quantity, total_price, payment_method, upi_id)
            update_stock(selected_product, quantity)
            st.success("🎉 Order placed successfully!")
            st.balloons()

# ---------------- ADMIN LOGIN ----------------
elif choice == "Admin Login":
    st.subheader("🔐 Admin Panel Login")

    if "admin_logged" not in st.session_state:
        st.session_state.admin_logged = False

    username = st.text_input("Admin Username")
    password = st.text_input("Admin Password", type="password")

    if st.button("Login"):
        if username == "divakar@1011" and password == "divakar1011":
            st.session_state.admin_logged = True
            st.success("✅ Login Successful!")
        else:
            st.error("❌ Invalid Username or Password")

    if st.session_state.admin_logged:

        admin_menu = st.radio("Admin Options", ["Add Product", "View Products", "View Orders"])

        # Add Product
        if admin_menu == "Add Product":
            st.subheader("➕ Add New Product")

            pname = st.text_input("Product Name")
            pprice = st.number_input("Price (₹)", min_value=1)
            pstock = st.number_input("Stock (Liters)", min_value=1)

            if st.button("Add Product Now"):
                if pname == "":
                    st.error("❌ Product Name must be filled!")
                else:
                    add_product(pname, pprice, pstock)
                    st.success("✅ Product Added Successfully!")

        # View Products
        elif admin_menu == "View Products":
            st.subheader("📋 Product List")
            products = get_products()
            df = pd.DataFrame(products, columns=["ID", "Product Name", "Price (₹)", "Stock (L)"])
            st.dataframe(df, use_container_width=True)

        # View Orders
        elif admin_menu == "View Orders":
            st.subheader("📦 Customer Orders List")
            orders = get_orders()
            df = pd.DataFrame(orders, columns=["ID", "Customer Name", "Phone", "Product", "Quantity", "Total Price"])
            st.dataframe(df, use_container_width=True)


            # Add Product
            if admin_menu == "Add Product":
                st.subheader("➕ Add New Product")

                pname = st.text_input("Product Name")
                pprice = st.number_input("Price (₹)", min_value=1)
                pstock = st.number_input("Stock (Liters)", min_value=1)

                if st.button("Add Product Now"):
                    add_product(pname, pprice, pstock)
                    st.success("✅ Product Added Successfully!")

            # View Products
            elif admin_menu == "View Products":
                st.subheader("📋 Product List")
                products = get_products()
                df = pd.DataFrame(products, columns=["ID", "Product Name", "Price (₹)", "Stock (L)"])
                st.dataframe(df, use_container_width=True)

            # View Orders
            elif admin_menu == "View Orders":
                st.subheader("📦 Customer Orders List")
                orders = get_orders()
                df = pd.DataFrame(orders, columns=["ID", "Customer Name", "Phone", "Product", "Quantity", "Total Price"])
                st.dataframe(df, use_container_width=True)

        else:
            st.error("❌ Invalid Admin Username or Password!")

