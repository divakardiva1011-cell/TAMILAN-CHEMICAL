import streamlit as st
import sqlite3
import pandas as pd
import base64
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Phenyl Shop", page_icon="🧴", layout="wide")

# ---------------- AUTO REFRESH FOR SLIDESHOW ----------------
st_autorefresh(interval=3000, key="slider")  # 3 seconds refresh

# ---------------- DATABASE ----------------
conn = sqlite3.connect("phenyl_shop.db", check_same_thread=False)
cur = conn.cursor()

# ---------------- CREATE TABLES ----------------
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
    cur.execute("""
        INSERT INTO orders(customer_name, phone, address, pincode, product, quantity, total_price, payment_method, upi_id)
        VALUES(?,?,?,?,?,?,?,?,?)
    """, (customer_name, phone, address, pincode, product, quantity, total_price, payment_method, upi_id))
    conn.commit()

def get_orders():
    cur.execute("SELECT * FROM orders")
    return cur.fetchall()

def update_stock(product_name, quantity):
    cur.execute("UPDATE products SET stock = stock - ? WHERE name = ?", (quantity, product_name))
    conn.commit()

# ---------------- DEFAULT PRODUCTS ----------------
cur.execute("SELECT COUNT(*) FROM products")
count = cur.fetchone()[0]

if count == 0:
    add_product("Lemon Phenyl", 80, 50)
    add_product("Pine Phenyl", 90, 40)
    add_product("Rose Phenyl", 85, 30)

# ---------------- CSS DESIGN ----------------
st.markdown("""
<style>
.slider-box {
    position: relative;
    width: 100%;
    height: 320px;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0px 4px 25px rgba(0,0,0,0.2);
    margin-bottom: 25px;
}

.slider-box img {
    width: 100%;
    height: 320px;
    object-fit: cover;
}

.text-overlay {
    position: absolute;
    top: 25px;
    left: 30px;
    color: white;
    background: rgba(0,0,0,0.45);
    padding: 18px;
    border-radius: 15px;
    font-size: 22px;
    font-weight: bold;
    max-width: 80%;
}

.text-overlay small {
    font-size: 16px;
    font-weight: normal;
}
</style>
""", unsafe_allow_html=True)

# ---------------- UI ----------------
st.title("🧴 TAMILAN CHEMICALS")

menu = ["Home", "Customer Order", "Admin Login"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------- HOME PAGE ----------------
if choice == "Home":

    # -------- SLIDESHOW IMAGES --------
    images = ["img1.jpg", "img2.jpg", "img3.jpg", "img4.jpg"]

    if "img_index" not in st.session_state:
        st.session_state.img_index = 0

    img_file = images[st.session_state.img_index]

    # update index
    st.session_state.img_index = (st.session_state.img_index + 1) % len(images)

    # convert image to base64
    try:
        img_base64 = base64.b64encode(open(img_file, "rb").read()).decode()
    except:
        img_base64 = ""

    # show slider box
    if img_base64 != "":
        st.markdown(f"""
        <div class="slider-box">
            <img src="data:image/jpg;base64,{img_base64}">
            <div class="text-overlay">
                ✨ Welcome to TAMILAN CHEMICAL <br>
                <small>We provide best phenyl products for home and industrial cleaning.</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Slideshow images not found! Please add img1.jpg img2.jpg img3.jpg img4.jpg in same folder.")

    st.markdown("## 🛒 Available Products")

    products = get_products()
    df = pd.DataFrame(products, columns=["ID", "Product Name", "Price (₹)", "Stock (L)"])
    st.dataframe(df, use_container_width=True)

# ---------------- CUSTOMER ORDER PAGE ----------------
elif choice == "Customer Order":
    st.subheader("📦 Place Your Order")

    name = st.text_input("Customer Name", key="cust_name")
    phone = st.text_input("Mobile Number", key="cust_phone")
    address = st.text_area("Delivery Address", key="cust_address")
    pincode = st.text_input("Pincode", key="cust_pincode")

    payment_method = st.selectbox("Payment Method", ["Cash On Delivery", "UPI Payment"], key="cust_payment")
    upi_id = st.text_input("UPI ID (Only if UPI Payment)", key="cust_upi")

    products = get_products()
    product_names = [p[1] for p in products]

    selected_product = st.selectbox("Select Product", product_names, key="cust_product")

    quantity = st.number_input("Quantity (Liters)", min_value=1, max_value=100, key="cust_quantity")

    # Get selected product data
    selected_data = [p for p in products if p[1] == selected_product][0]
    price = selected_data[2]
    stock = selected_data[3]

    st.info(f"💰 Price per Liter: ₹{price}")
    st.warning(f"📦 Available Stock: {stock} Liters")

    total_price = price * quantity
    st.success(f"✅ Total Price: ₹{total_price}")

    if st.button("Confirm Order", key="confirm_order"):
        if name.strip() == "" or phone.strip() == "" or address.strip() == "" or pincode.strip() == "":
            st.error("❌ Please fill all details")
        elif quantity > stock:
            st.error("❌ Stock not available for this quantity!")
        else:
            place_order(name, phone, address, pincode, selected_product, quantity, total_price, payment_method, upi_id)
            update_stock(selected_product, quantity)
            st.success("🎉 Order placed successfully!")
            st.balloons()

# ---------------- ADMIN LOGIN PAGE ----------------
elif choice == "Admin Login":
    st.subheader("🔐 Admin Panel Login")

    if "admin_logged" not in st.session_state:
        st.session_state.admin_logged = False

    username = st.text_input("Admin Username", key="admin_user")
    password = st.text_input("Admin Password", type="password", key="admin_pass")

    if st.button("Login", key="admin_login_btn"):
        if username == "divakar@1011" and password == "divakar1011":
            st.session_state.admin_logged = True
            st.success("✅ Login Successful!")
        else:
            st.error("❌ Invalid Username or Password")

    if st.session_state.admin_logged:
        st.success("🎉 Welcome Admin!")

        admin_menu = st.radio("Admin Options", ["Add Product", "View Products", "View Orders"], key="admin_menu")

        # Add Product
        if admin_menu == "Add Product":
            st.subheader("➕ Add New Product")

            pname = st.text_input("Product Name", key="new_product_name")
            pprice = st.number_input("Price (₹)", min_value=1, key="new_product_price")
            pstock = st.number_input("Stock (Liters)", min_value=1, key="new_product_stock")

            if st.button("Add Product Now", key="add_product_btn"):
                if pname.strip() == "":
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

            df = pd.DataFrame(
                orders,
                columns=["ID", "Customer Name", "Phone", "Address", "Pincode",
                         "Product", "Quantity", "Total Price", "Payment Method", "UPI ID"]
            )

            st.dataframe(df, use_container_width=True)

