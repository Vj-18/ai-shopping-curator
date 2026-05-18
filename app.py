import streamlit as st
import sqlite3
import bcrypt
import requests
from PIL import Image

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Curatrix",
    page_icon="✨",
    layout="wide"
)

# ============================================================
# SESSION STATE DEFAULTS
# ============================================================

DEFAULTS = {
    "logged_in":           False,
    "user_email":          "",
    "cart":                [],
    "wishlist":            [],
    "page":                "home",
    "current_product":     None,
    "liked_brands":        [],
    "show_image_uploader": False,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.stApp { background-color: #0B0B0B; }

.logo {
    text-align: center;
    color: #F5E6D3;
    font-size: 52px;
    font-weight: bold;
    margin-top: 10px;
}

.subtitle {
    text-align: center;
    color: #B8B8B8;
    font-size: 20px;
    margin-bottom: 30px;
}

.stTextInput > div > div > input {
    background-color: #161616;
    color: white;
    border-radius: 14px;
    border: 1px solid #2A2A2A;
    padding: 16px;
    font-size: 18px;
}

.stButton > button {
    background: none;
    color: white;
    border: none;
    font-size: 16px;
    font-weight: 500;
}

.stButton > button:hover { color: #D4B08C; }

.brand {
    color: #8A8A8A;
    font-size: 13px;
    margin-top: 12px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.product-title {
    color: white;
    font-size: 22px;
    font-weight: 600;
    margin-top: 6px;
}

.price {
    color: #D4B08C;
    font-size: 20px;
    margin-top: 6px;
    margin-bottom: 10px;
}

.heading {
    color: white;
    font-size: 36px;
    font-weight: bold;
    margin-top: 30px;
    margin-bottom: 20px;
}

.product-card {
    padding: 12px;
    border-radius: 18px;
    transition: 0.3s;
}

.product-card:hover { background-color: #141414; }

</style>
""", unsafe_allow_html=True)

# ============================================================
# DATABASE
# ============================================================

def connect_db():
    conn = sqlite3.connect("curatrix.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL,
            email    TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            email     TEXT    NOT NULL,
            items     TEXT    NOT NULL,
            total     INTEGER NOT NULL,
            placed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def create_user(username: str, email: str, password: str) -> bool:
    """Hash password with bcrypt then store. Returns False if email exists."""
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        conn = connect_db()
        conn.execute(
            "INSERT INTO users(username, email, password) VALUES(?, ?, ?)",
            (username, email, hashed)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def get_user(email: str, password: str):
    """Fetch user and verify bcrypt hash. Returns row or None."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()
    if user and bcrypt.checkpw(password.encode(), user[3].encode()):
        return user
    return None


def save_order(email: str, items: list, total: int):
    import json
    summary = json.dumps([
        {"name": i["product"]["name"], "size": i["size"], "qty": i["qty"]}
        for i in items
    ])
    conn = connect_db()
    conn.execute(
        "INSERT INTO orders(email, items, total) VALUES(?, ?, ?)",
        (email, summary, total)
    )
    conn.commit()
    conn.close()


def get_orders(email: str) -> list:
    import json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT items, total, placed_at FROM orders WHERE email=? ORDER BY placed_at DESC",
        (email,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"items": json.loads(r[0]), "total": r[1], "placed_at": r[2]} for r in rows]

# ============================================================
# DATA
# ============================================================

PRODUCTS = [
    {"brand": "NIKE",   "name": "Nike Dunk Low Retro Men's Shoes",    "price": 8295,  "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff", "link": "https://www.myntra.com/",    "retailer": "Myntra",   "category": "Shoes"},
    {"brand": "NIKE",   "name": "Nike Air Force 1 '07 Sneakers",      "price": 7495,  "image": "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519","link": "https://www.myntra.com/",    "retailer": "Myntra",   "category": "Shoes"},
    {"brand": "NIKE",   "name": "Nike Club Fleece Basketball Hoodie",  "price": 3995,  "image": "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c","link": "https://www.myntra.com/",    "retailer": "Myntra",   "category": "Hoodies"},
    {"brand": "NIKE",   "name": "Nike Tech Men Fleece Hoodie",         "price": 6296,  "image": "https://images.unsplash.com/photo-1556821840-3a63f15732ce",  "link": "https://www.myntra.com/",    "retailer": "Myntra",   "category": "Hoodies"},
    {"brand": "ADIDAS", "name": "Adidas Ultraboost Running Shoes",     "price": 8999,  "image": "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77","link": "https://www.myntra.com/",    "retailer": "Myntra",   "category": "Shoes"},
    {"brand": "ADIDAS", "name": "Adidas Pureboost Running Shoes",      "price": 7409,  "image": "https://images.unsplash.com/photo-1543508282-6319a3e2621f",  "link": "https://www.myntra.com/",    "retailer": "Myntra",   "category": "Shoes"},
    {"brand": "PUMA",   "name": "Puma RS-X Reinvention Sneakers",      "price": 9999,  "image": "https://images.unsplash.com/photo-1608231387042-66d1773070a5","link": "https://www.flipkart.com/",  "retailer": "Flipkart", "category": "Shoes"},
    {"brand": "PUMA",   "name": "Puma RS-X Geek Sneakers",             "price": 10999, "image": "https://images.unsplash.com/photo-1579338559194-a162d19bf842", "link": "https://www.flipkart.com/",  "retailer": "Flipkart", "category": "Shoes"},
    {"brand": "H&M",    "name": "H&M Minimal Slip Dress",              "price": 2999,  "image": "https://images.unsplash.com/photo-1496747611176-843222e1e57c","link": "https://www2.hm.com/en_in/", "retailer": "H&M",      "category": "Dresses"},
    {"brand": "ZARA",   "name": "Zara Beige Trench Coat",              "price": 5999,  "image": "https://images.unsplash.com/photo-1483985988355-763728e1935b","link": "https://www.zara.com/in/",   "retailer": "Zara",     "category": "Jackets"},
]

CATEGORIES = ["All", "Shoes", "Hoodies", "Jackets", "Dresses"]

SIZES = {
    "Shoes":   ["UK 6", "UK 7", "UK 8", "UK 9", "UK 10", "UK 11"],
    "Hoodies": ["XS", "S", "M", "L", "XL", "XXL"],
    "Jackets": ["XS", "S", "M", "L", "XL", "XXL"],
    "Dresses": ["XS", "S", "M", "L", "XL"],
}

PRICE_COMPARISON = {
    "Nike Dunk Low Retro Men's Shoes":   {"Myntra": 8295,  "Nike.com": 8995,  "Flipkart": 8499, "Amazon": 8695},
    "Nike Air Force 1 '07 Sneakers":     {"Myntra": 7495,  "Nike.com": 7995,  "Flipkart": 7295, "Amazon": 7599},
    "Nike Club Fleece Basketball Hoodie":{"Myntra": 3995,  "Nike.com": 4295,  "Flipkart": 3795, "Amazon": 3899},
    "Adidas Ultraboost Running Shoes":   {"Myntra": 8999,  "Adidas.in": 17999,"Flipkart": 8549, "Amazon": 9199},
    "Puma RS-X Reinvention Sneakers":    {"Flipkart": 9999,"Puma.in": 9999,   "Myntra": 10999,  "Amazon": 9499},
}

WEBSITE_LINKS = {
    "Myntra":    "https://www.myntra.com/",
    "Flipkart":  "https://www.flipkart.com/",
    "Amazon":    "https://www.amazon.in/",
    "Nike.com":  "https://www.nike.com/in/",
    "Adidas.in": "https://www.adidas.co.in/",
    "Puma.in":   "https://in.puma.com/",
}

DISCOUNT_CODES = {
    "CURATRIX10": 10,
    "FASHION20":  20,
    "NEWUSER15":  15,
}

# ============================================================
# AI STYLE TIPS  — real Claude API call
# ============================================================

def get_style_tips(product_name: str, product_brand: str, product_category: str) -> list:
    """
    Calls Claude claude-haiku-4-5-20251001 for dynamic outfit suggestions.
    Falls back to generic tips if API key is missing or call fails.
    Set ANTHROPIC_API_KEY in your Streamlit secrets (.streamlit/secrets.toml).
    """
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ValueError("No API key")

        prompt = (
            f"You are a fashion stylist. Give exactly 3 short, specific outfit styling tips "
            f"for the '{product_name}' by {product_brand} (category: {product_category}). "
            f"Each tip must be one sentence, practical, and trendy for Indian urban fashion in 2025. "
            f"Reply ONLY as a JSON array of 3 strings with no extra text. "
            f'Example: ["Tip one.", "Tip two.", "Tip three."]'
        )

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":         api_key,
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json",
            },
            json={
                "model":    "claude-haiku-4-5-20251001",
                "max_tokens": 200,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=10,
        )

        import json
        text = response.json()["content"][0]["text"].strip()
        tips = json.loads(text)
        if isinstance(tips, list) and len(tips) >= 3:
            return tips[:3]

    except Exception:
        pass

    # Fallback
    return [
        "Style with neutral tones for a clean, versatile look",
        "Add minimal accessories to let the piece speak for itself",
        "Pair with white sneakers for an effortless everyday finish",
    ]

# ============================================================
# HELPERS
# ============================================================

def get_personalized_feed() -> list:
    return [p for p in PRODUCTS if p["brand"] in st.session_state.liked_brands]


def filter_products(query: str, category: str, sort: str) -> list:
    result = PRODUCTS
    if category != "All":
        result = [p for p in result if p["category"] == category]
    if query:
        result = [p for p in result if query.lower() in p["name"].lower()]
    if sort == "Price: Low to High":
        result = sorted(result, key=lambda p: p["price"])
    elif sort == "Price: High to Low":
        result = sorted(result, key=lambda p: p["price"], reverse=True)
    return result


def add_to_cart(product: dict, size: str, qty: int = 1):
    for item in st.session_state.cart:
        if item["product"]["name"] == product["name"] and item["size"] == size:
            item["qty"] += qty
            return
    st.session_state.cart.append({"product": product, "size": size, "qty": qty})


def remove_from_cart(index: int):
    st.session_state.cart.pop(index)
    st.rerun()


def toggle_wishlist(product: dict):
    names = [p["name"] for p in st.session_state.wishlist]
    if product["name"] in names:
        st.session_state.wishlist = [p for p in st.session_state.wishlist if p["name"] != product["name"]]
    else:
        st.session_state.wishlist.append(product)


def is_wishlisted(product: dict) -> bool:
    return product["name"] in [p["name"] for p in st.session_state.wishlist]


def go_to(page: str, product: dict = None):
    st.session_state.page = page
    if product:
        st.session_state.current_product = product
        if product["brand"] not in st.session_state.liked_brands:
            st.session_state.liked_brands.append(product["brand"])
    st.rerun()


def cart_total() -> int:
    return sum(i["product"]["price"] * i["qty"] for i in st.session_state.cart)


def apply_discount(total: int, code: str):
    code = code.strip().upper()
    if code in DISCOUNT_CODES:
        pct    = DISCOUNT_CODES[code]
        saving = int(total * pct / 100)
        return total - saving, f"✅ {pct}% discount applied! You save ₹{saving:,}"
    return total, "❌ Invalid discount code"

# ============================================================
# UI COMPONENTS
# ============================================================

def render_header(subtitle: str = "Discover Fashion Smarter"):
    st.markdown('<div class="logo">✨ Curatrix</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">{subtitle}</div>', unsafe_allow_html=True)


def render_product_meta(product: dict):
    st.markdown(f"""
        <div class="brand">{product['brand']}</div>
        <div class="product-title">{product['name']}</div>
        <div class="price">₹{product['price']:,}</div>
    """, unsafe_allow_html=True)


def render_product_grid(products_list: list):
    if not products_list:
        st.write("No products found.")
        return

    cols = st.columns(4, gap="large")
    for i, product in enumerate(products_list):
        with cols[i % 4]:
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            st.image(product["image"], use_container_width=True)

            heart    = "❤️" if is_wishlisted(product) else "🤍"
            wl_col, name_col = st.columns([1, 5])
            with wl_col:
                if st.button(heart, key=f"wl_{product['name']}_{i}"):
                    toggle_wishlist(product)
                    st.rerun()
            with name_col:
                if st.button(product["name"], key=f"view_{product['name']}_{i}"):
                    go_to("product", product)

            render_product_meta(product)

            size_options = SIZES.get(product["category"], ["S", "M", "L", "XL"])
            size = st.selectbox("Size", size_options, key=f"size_{product['name']}_{i}", label_visibility="collapsed")

            if st.button("Add to Cart", key=f"cart_{product['name']}_{i}"):
                add_to_cart(product, size)
                st.success(f"Added {size} to cart!")

            st.markdown(
                f'<a href="{product["link"]}" target="_blank" style="font-size:12px;color:#D4B08C;">🔗 {product.get("retailer","Store")}</a>',
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# PAGES
# ============================================================

def page_login():
    render_header("Luxury Fashion Discovery Platform")

    choice = st.selectbox("Choose Option", ["Login", "Signup"])

    if choice == "Signup":
        username = st.text_input("Username")
        email    = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Signup"):
            if not username or not email or not password:
                st.error("Please fill all fields.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                if create_user(username, email, password):
                    st.success("Account created! Please login.")
                else:
                    st.error("Email already registered.")

    else:
        email    = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = get_user(email, password)
            if user:
                st.session_state.logged_in  = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Invalid credentials.")


def page_navbar():
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("🏠 Home"):
            go_to("home")
    with c2:
        if st.button(f"🛒 Cart ({len(st.session_state.cart)})"):
            go_to("cart")
    with c3:
        if st.button(f"❤️ Wishlist ({len(st.session_state.wishlist)})"):
            go_to("wishlist")
    with c4:
        if st.button("📦 Orders"):
            go_to("orders")
    with c5:
        if st.button("🚪 Logout"):
            for key, value in DEFAULTS.items():
                st.session_state[key] = value
            st.rerun()
    st.markdown("---")


def page_home():
    search_col, icon_col = st.columns([20, 1])
    with search_col:
        search = st.text_input("", placeholder="Search Nike, Adidas, Puma...", label_visibility="collapsed")
    with icon_col:
        st.markdown("<div style='margin-top:6px;font-size:28px;' title='Image Search'>📷</div>", unsafe_allow_html=True)
        if st.button("", key="img_toggle", help="Search by image"):
            st.session_state.show_image_uploader = not st.session_state.show_image_uploader
            st.rerun()

    if st.session_state.show_image_uploader:
        uploaded = st.file_uploader("Upload fashion image", type=["jpg","jpeg","png"], label_visibility="collapsed")
        if uploaded:
            st.image(Image.open(uploaded), width=200)
            st.success("Image uploaded — searching for similar styles...")

    f1, f2 = st.columns([3, 1])
    with f1:
        category = st.radio("Category", CATEGORIES, horizontal=True, label_visibility="collapsed")
    with f2:
        sort = st.selectbox("Sort", ["Default", "Price: Low to High", "Price: High to Low"], label_visibility="collapsed")

    render_product_grid(filter_products(search, category, sort))


def page_product():
    product = st.session_state.current_product
    if not product:
        go_to("home")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.image(product["image"], use_container_width=True)

    with col2:
        render_product_meta(product)

        size_options = SIZES.get(product["category"], ["S", "M", "L", "XL"])
        size = st.selectbox("Select Size", size_options)

        btn1, btn2, btn3 = st.columns(3)
        with btn1:
            if st.button("🛒 Add to Cart"):
                add_to_cart(product, size)
                st.success("Added to Cart")
        with btn2:
            heart = "❤️ Saved" if is_wishlisted(product) else "🤍 Wishlist"
            if st.button(heart):
                toggle_wishlist(product)
                st.rerun()
        with btn3:
            st.markdown(
                f'<a href="{product["link"]}" target="_blank" style="display:inline-block;background:#D4B08C;color:#0B0B0B;padding:10px 14px;border-radius:10px;font-weight:700;text-decoration:none;font-size:13px;margin-top:4px;">🔗 {product.get("retailer","Buy")}</a>',
                unsafe_allow_html=True
            )

        st.markdown("---")
        st.markdown("## ✨ AI Style Suggestions")
        with st.spinner("Getting AI style tips..."):
            tips = get_style_tips(product["name"], product["brand"], product["category"])
        for tip in tips:
            st.success(tip)

        st.markdown("---")
        st.markdown("## 💰 Price Comparison")
        if product["name"] in PRICE_COMPARISON:
            prices = PRICE_COMPARISON[product["name"]]
            lowest = min(prices.values())
            for site, price in prices.items():
                if price == lowest:
                    st.success(f"✅ {site}: ₹{price:,} — Best Deal")
                else:
                    st.write(f"{site}: ₹{price:,}")
                if site in WEBSITE_LINKS:
                    st.markdown(f"[Open {site}]({WEBSITE_LINKS[site]})")

    st.markdown("---")
    st.markdown("## ✨ Recommended For You")
    personalized = [p for p in get_personalized_feed() if p["name"] != product["name"]]
    if personalized:
        rec_cols = st.columns(4)
        for i, item in enumerate(personalized):
            with rec_cols[i % 4]:
                st.image(item["image"], use_container_width=True)
                render_product_meta(item)
    else:
        st.write("Browse more products to get personalised picks.")


def page_cart():
    st.markdown('<div class="heading">🛒 Your Cart</div>', unsafe_allow_html=True)

    if not st.session_state.cart:
        st.write("Your cart is empty.")
        return

    for i, item in enumerate(st.session_state.cart):
        p = item["product"]
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(p["image"], width=220)
        with col2:
            render_product_meta(p)
            st.write(f"**Size:** {item['size']}")

            q1, q2, q3 = st.columns([1, 1, 2])
            with q1:
                if st.button("−", key=f"dec_{i}"):
                    if item["qty"] > 1:
                        item["qty"] -= 1
                    else:
                        remove_from_cart(i)
                    st.rerun()
            with q2:
                st.write(f"**{item['qty']}**")
            with q3:
                if st.button("+", key=f"inc_{i}"):
                    item["qty"] += 1
                    st.rerun()

            st.write(f"Subtotal: ₹{p['price'] * item['qty']:,}")
            if st.button("Remove", key=f"remove_{i}"):
                remove_from_cart(i)

    st.markdown("---")

    code_col, apply_col = st.columns([3, 1])
    with code_col:
        discount_code = st.text_input("Discount Code", placeholder="Try: CURATRIX10 / FASHION20 / NEWUSER15")
    with apply_col:
        st.markdown("<br>", unsafe_allow_html=True)
        apply_btn = st.button("Apply")

    final_total = cart_total()
    if apply_btn and discount_code:
        final_total, msg = apply_discount(cart_total(), discount_code)
        st.session_state["applied_code"] = discount_code
        st.info(msg)
    elif "applied_code" in st.session_state:
        final_total, _ = apply_discount(cart_total(), st.session_state["applied_code"])

    st.subheader(f"Total: ₹{final_total:,}")
    if st.button("Proceed to Checkout"):
        st.session_state["checkout_total"] = final_total
        go_to("checkout")


def page_wishlist():
    st.markdown('<div class="heading">❤️ Your Wishlist</div>', unsafe_allow_html=True)
    if not st.session_state.wishlist:
        st.write("Your wishlist is empty — hit 🤍 on any product to save it.")
        return
    cols = st.columns(4, gap="large")
    for i, product in enumerate(st.session_state.wishlist):
        with cols[i % 4]:
            st.image(product["image"], use_container_width=True)
            render_product_meta(product)
            if st.button("Remove", key=f"wl_remove_{i}"):
                toggle_wishlist(product)
                st.rerun()
            if st.button("Add to Cart", key=f"wl_cart_{i}"):
                default_size = SIZES.get(product["category"], ["M"])[0]
                add_to_cart(product, default_size)
                st.success(f"Added with size {default_size} — update in cart if needed.")


def page_checkout():
    st.markdown('<div class="heading">💳 Checkout</div>', unsafe_allow_html=True)

    name    = st.text_input("Full Name")
    st.text_input("Card Number")
    c1, c2  = st.columns(2)
    with c1:
        st.text_input("Expiry Date (MM/YY)")
    with c2:
        st.text_input("CVV", type="password")
    address = st.text_area("Billing Address")
    st.selectbox("Payment Method", ["Credit Card", "Debit Card", "UPI", "Cash on Delivery"])

    st.markdown("---")
    total = st.session_state.get("checkout_total", cart_total())
    st.subheader(f"Total Payable: ₹{total:,}")

    if st.button("Place Order"):
        if not name or not address:
            st.error("Please fill your name and address.")
        else:
            save_order(st.session_state.user_email, st.session_state.cart, total)
            st.session_state.cart = []
            st.session_state.pop("applied_code", None)
            st.session_state.pop("checkout_total", None)
            go_to("success")


def page_orders():
    st.markdown('<div class="heading">📦 Order History</div>', unsafe_allow_html=True)
    orders = get_orders(st.session_state.user_email)
    if not orders:
        st.write("No orders placed yet.")
        return
    for order in orders:
        with st.expander(f"🗓 {order['placed_at']}  —  ₹{order['total']:,}"):
            for item in order["items"]:
                st.write(f"• {item['name']}  |  Size: {item['size']}  |  Qty: {item['qty']}")


def page_success():
    st.balloons()
    st.markdown("""
        <div style="text-align:center; padding:40px;">
            <h1 style="color:#F5E6D3; font-size:55px;">🎉 Order Placed!</h1>
            <p style="color:white; font-size:22px;">Your fashion order has been confirmed.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Continue Shopping"):
        go_to("home")

# ============================================================
# ROUTER
# ============================================================

PAGES = {
    "home":     page_home,
    "product":  page_product,
    "cart":     page_cart,
    "wishlist": page_wishlist,
    "checkout": page_checkout,
    "orders":   page_orders,
    "success":  page_success,
}

if not st.session_state.logged_in:
    page_login()
else:
    render_header()
    page_navbar()
    PAGES.get(st.session_state.page, page_home)()