import streamlit as st
import sqlite3
import pandas as pd
import base64
import qrcode
from io import BytesIO
from streamlit_autorefresh import st_autorefresh
import urllib.parse

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="TAMILAN CHEMICALS", page_icon="🧴", layout="wide")

# ---------------- CSS DESIGN ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0a0f2c, #0b3d2e, #2b1055);
    background-attachment: fixed;
    color: white;
    font-family: Arial;
}

h1,h2,h3,h4,h5,h6,p,label {
    color: white !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(0,0,0,0.45);
    border-right: 2px solid rgba(255,255,255,0.08);
}

/* Remove default box background */
div[data-testid="stVerticalBlock"] > div {
    background: transparent !important;
    padding: 0px !important;
    box-shadow: none !important;
}

/* Buttons */
.stButton button {
    background: linear-gradient(90deg, #ff4b2b, #ff416c);
    color: white;
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: bold;
    border: none;
    transition: 0.3s;
}

.stButton button:hover {
    transform: scale(1.05);
    background: linear-gradient(90deg, #00c6ff, #0072ff);
}

/* Slider Box */
.slider-box {
    position: relative;
    width: 100%;
    height: 380px;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0px 0px 30px rgba(0,0,0,0.6);
    margin-bottom: 25px;
}

.slider-box img {
    width: 100%;
    height: 380px;
    object-fit: cover;
}

/* Overlay Text */
.overlay-text {
    position: absolute;
    top: 30px;
    left: 30px;
    background: rgba(0,0,0,0.55);
    padding: 20px;
    border-radius: 15px;
    font-size: 22px;
    font-weight: bold;
    max-width: 70%;
}

.overlay-text small {
    display: block;
    font-size: 15px;
    font-weight: normal;
    margin-top: 5px;
    color: #ddd;
}

/* Contact Box */
.contact-box {
    background: rgba(255,255,255,0.10);
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0px 0px 20px rgba(0,0,0,0.4);
    margin-top: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- AUTO REFRESH SLIDER ----------------
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

def delete_product(product_id):
    cur.execute("DELETE FROM products WHERE id=?", (product_id,))
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

def generate_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    return buf.getvalue()

# ---------------- DEFAULT PRODUCTS ----------------
cur.execute("SELECT COUNT(*) FROM products")
count = cur.fetchone()[0]

if count == 0:
    add_product("Lemon Phenyl", 80, 50)
    add_product("Pine Phenyl", 90, 40)
    add_product("Rose Phenyl", 85, 30)
    add_product("Lavender Phenyl", 100, 20)

# ---------------- TITLE CENTER ----------------
st.markdown("""
<h1 style='text-align: center; font-size: 55px; font-weight: 900; color: white;
text-shadow: 2px 2px 15px rgba(0,0,0,0.9);'>
🧴 TAMILAN CHEMICALS
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<h4 style='text-align: center; font-size: 20px; font-weight: 600; color: #f1f1f1;'>
✨ Best Phenyl Cleaning Products | Home & Industrial Use
</h4>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ---------------- SIDEBAR MENU ----------------
st.sidebar.markdown("## 📌 MENU")
section = st.sidebar.radio("Select Page", ["🏠 Home", "🛒 Customer Order", "📞 Contact", "🔐 Admin Login"])

# ---------------- HOME PAGE ----------------
if section == "🏠 Home":

    # Add more than 10 images here
    images = [
        "img1.jpg", "img2.jpg", "img3.jpg", "img4.jpg", "img5.jpg",
        "img6.jpg", "img7.jpg", "img8.jpg", "img9.jpg", "img10.jpg",
        "img11.jpg", "img12.jpg"
    ]

    if "img_index" not in st.session_state:
        st.session_state.img_index = 0

    img_file = images[st.session_state.img_index]
    st.session_state.img_index = (st.session_state.img_index + 1) % len(images)

    try:
        img_base64 = base64.b64encode(open(img_file, "rb").read()).decode()
        st.markdown(f"""
        <div class="slider-box">
            <img src="data:image/jpg;base64,{img_base64}">
            <div class="overlay-text">
            </div>
        </div>
        """, unsafe_allow_html=True)
    except:
        st.warning("⚠️ Images not found! Add img1.jpg ... img12.jpg in same folder.")

    st.markdown("## 🛒 Available Products")

    products = get_products()
    df = pd.DataFrame(products, columns=["ID", "Product Name", "Price (₹)", "Stock (L)"])
    st.dataframe(df, use_container_width=True)

# ---------------- CUSTOMER ORDER PAGE ----------------
elif section == "🛒 Customer Order":

    st.subheader("📦 Place Your Order")

    name = st.text_input("Customer Name")
    phone = st.text_input("Mobile Number")
    address = st.text_area("Delivery Address")
    pincode = st.text_input("Pincode")

    products = get_products()
    product_names = [p[1] for p in products]

    selected_product = st.selectbox("Select Product", product_names)
    quantity = st.number_input("Quantity (Liters)", min_value=1, max_value=100)

    selected_data = [p for p in products if p[1] == selected_product][0]
    price = selected_data[2]
    stock = selected_data[3]

    st.info(f"💰 Price per Liter: ₹{price}")
    st.warning(f"📦 Available Stock: {stock} Liters")

    total_price = price * quantity
    st.success(f"✅ Total Price: ₹{total_price}")

    payment_method = st.selectbox("Payment Method", ["Cash On Delivery", "UPI Payment"])
    upi_id = "divakardiva1011@oksbi"

    # ---------------- UPI QR DISPLAY ----------------
    if payment_method == "UPI Payment":
        upi_link = f"upi://pay?pa={upi_id}&pn=TAMILAN%20CHEMICALS&am={total_price}&cu=INR"
        qr_img = generate_qr(upi_link)
        st.image(qr_img, caption="📌 Scan & Pay using GPay / PhonePe / Paytm", width=250)

    # ---------------- WHATSAPP ORDER LINK ----------------
    whatsapp_number = "917448866665"  # CHANGE THIS NUMBER

    message = f"""
    🧴 TAMILAN CHEMICALS ORDER
    ------------------------
    Name: {name}
    Phone: {phone}
    Address: {address}
    Pincode: {pincode}
    Product: {selected_product}
    Quantity: {quantity} Liters
    Total Price: ₹{total_price}
    Payment: {payment_method}
    """

    whatsapp_url = f"https://wa.me/{whatsapp_number}?text={urllib.parse.quote(message)}"

    st.markdown(f"📲 **WhatsApp Order Link:** [Click Here to Order]({whatsapp_url})")

    if st.button("✅ Confirm Order"):
        if name.strip() == "" or phone.strip() == "" or address.strip() == "" or pincode.strip() == "":
            st.error("❌ Please fill all details")
        elif quantity > stock:
            st.error("❌ Stock not available for this quantity!")
        else:
            place_order(name, phone, address, pincode, selected_product, quantity, total_price, payment_method, upi_id)
            update_stock(selected_product, quantity)
            st.success("🎉 Order placed successfully!")
            st.balloons()

# ---------------- CONTACT PAGE ----------------
elif section == "📞 Contact":

    st.subheader("📞 Contact Details")

    st.markdown("""
    <div class="contact-box">
    <h3>🏢 TAMILAN CHEMICALS</h3>
    <p>📍 Address: No 11B Periyar sale Rajiv Gandhi Nagar alapakkam Chennai-600116</p>
    <p>📞 Mobile: +91 74488666665/9514133444</p>
    <p>📧 Email: tamilanchemicals@gmail.com</p>
    <p>💳 UPI: divakardiva1011@oksbi</p>
    <p>🕒 Working Time: 9AM - 9PM</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------- ADMIN LOGIN PAGE ----------------
elif section == "🔐 Admin Login":

    st.subheader("🔐 Admin Panel Login")

    if "admin_logged" not in st.session_state:
        st.session_state.admin_logged = False

    username = st.text_input("Admin Username")
    password = st.text_input("Admin Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.admin_logged = True
            st.success("✅ Login Successful!")
        else:
            st.error("❌ Invalid Username or Password")

    if st.session_state.admin_logged:

        st.success("🎉 Welcome Admin!")

        admin_menu = st.radio("Admin Options", ["Add Product", "Delete Product", "View Products", "View Orders"])

        # Add Product
        if admin_menu == "Add Product":
            st.subheader("➕ Add New Product")

            pname = st.text_input("Product Name")
            pprice = st.number_input("Price (₹)", min_value=1)
            pstock = st.number_input("Stock (Liters)", min_value=1)

            if st.button("Add Product Now"):
                if pname.strip() == "":
                    st.error("❌ Product Name must be filled!")
                else:
                    add_product(pname, pprice, pstock)
                    st.success("✅ Product Added Successfully!")

        # Delete Product
        elif admin_menu == "Delete Product":
            st.subheader("🗑 Delete Product")

            products = get_products()
            df = pd.DataFrame(products, columns=["ID", "Product Name", "Price (₹)", "Stock (L)"])
            st.dataframe(df, use_container_width=True)

            pid = st.number_input("Enter Product ID to Delete", min_value=1)

            if st.button("Delete Now"):
                delete_product(pid)
                st.success("✅ Product Deleted Successfully!")

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
