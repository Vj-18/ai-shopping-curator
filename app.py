import streamlit as st
import sqlite3

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="Curatrix",
    page_icon="✨",
    layout="wide"
)

# -----------------------------------
# SESSION STATE
# -----------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "cart" not in st.session_state:
    st.session_state.cart = []

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_product" not in st.session_state:
    st.session_state.selected_product = None

# -----------------------------------
# CUSTOM CSS
# -----------------------------------

st.markdown("""
<style>

.stApp{
    background-color:#0B0B0B;
}

.logo{
    text-align:center;
    color:#F5E6D3;
    font-size:52px;
    font-weight:bold;
    margin-top:10px;
}

.subtitle{
    text-align:center;
    color:#B8B8B8;
    font-size:20px;
    margin-bottom:30px;
}

.stTextInput > div > div > input {
    background-color:#161616;
    color:white;
    border-radius:14px;
    border:1px solid #2A2A2A;
    padding:16px;
    font-size:18px;
}

.stButton>button {
    background:none;
    color:white;
    border:none;
    font-size:16px;
    font-weight:500;
}

.stButton>button:hover{
    color:#D4B08C;
}

.brand{
    color:#8A8A8A;
    font-size:13px;
    margin-top:12px;
    letter-spacing:1px;
    text-transform:uppercase;
}

.product-title{
    color:white;
    font-size:22px;
    font-weight:500;
    margin-top:4px;
}

.price{
    color:#D4B08C;
    font-size:19px;
    margin-top:8px;
    margin-bottom:10px;
}

.heading{
    color:white;
    font-size:36px;
    font-weight:bold;
    margin-top:30px;
    margin-bottom:20px;
}

.product-card{
    padding:12px;
    border-radius:18px;
    transition:0.3s;
}

.product-card:hover{
    background-color:#141414;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# DATABASE
# -----------------------------------

def connect_db():
    conn = sqlite3.connect("curatrix.db")
    return conn

# -----------------------------------
# AI RECOMMENDATIONS
# -----------------------------------

def get_fashion_recommendation(product_name):

    recommendations = {

        "Nike Air Max Sneakers":
        [
            "Pair with oversized joggers",
            "Style with Nike hoodie",
            "Add silver accessories"
        ],

        "Nike Sports Hoodie":
        [
            "Looks great with cargo pants",
            "Pair with white sneakers",
            "Add crossbody bag"
        ],

        "Adidas Ultraboost Shoes":
        [
            "Perfect with relaxed fit jeans",
            "Style with oversized tee",
            "Add black cap"
        ]
    }

    if product_name in recommendations:
        return recommendations[product_name]

    return [
        "Style with neutral colors",
        "Add trendy accessories",
        "Pair with minimal sneakers"
    ]

# -----------------------------------
# PRODUCTS
# -----------------------------------

products = [

    {
        "brand":"NIKE",
        "name":"Nike Air Max Sneakers",
        "price":8999,
        "image":"https://images.unsplash.com/photo-1542291026-7eec264c27ff"
    },

    {
        "brand":"NIKE",
        "name":"Nike Sports Hoodie",
        "price":3499,
        "image":"https://images.unsplash.com/photo-1503342217505-b0a15ec3261c"
    },

    {
        "brand":"ADIDAS",
        "name":"Adidas Ultraboost Shoes",
        "price":9999,
        "image":"https://images.unsplash.com/photo-1600185365483-26d7a4cc7519"
    },

    {
        "brand":"PUMA",
        "name":"Puma RS-X Sneakers",
        "price":6999,
        "image":"https://images.unsplash.com/photo-1542291026-7eec264c27ff"
    },

    {
        "brand":"H&M",
        "name":"H&M Minimal Dress",
        "price":2999,
        "image":"https://images.unsplash.com/photo-1495385794356-15371f348c31"
    }
]

# -----------------------------------
# PRICE COMPARISON
# -----------------------------------

price_comparison = {

    "Nike Air Max Sneakers": {
        "Nike Website": 8999,
        "Myntra": 8599,
        "Ajio": 8799,
        "Amazon": 8499
    },

    "Nike Sports Hoodie": {
        "Nike Website": 3499,
        "Myntra": 3299,
        "Ajio": 3399,
        "Amazon": 3199
    },

    "Adidas Ultraboost Shoes": {
        "Adidas Website": 9999,
        "Myntra": 9499,
        "Ajio": 9699,
        "Amazon": 9299
    }
}

# -----------------------------------
# WEBSITE LINKS
# -----------------------------------

website_links = {

    "Myntra":"https://www.myntra.com/",
    "Ajio":"https://www.ajio.com/",
    "Amazon":"https://www.amazon.in/",
    "Nike Website":"https://www.nike.com/in/",
    "Adidas Website":"https://www.adidas.co.in/"
}

# -----------------------------------
# LOGIN PAGE
# -----------------------------------

if st.session_state.logged_in == False:

    st.markdown(
        '<div class="logo">✨ Curatrix</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Luxury Fashion Discovery Platform</div>',
        unsafe_allow_html=True
    )

    choice = st.selectbox(
        "Choose Option",
        ["Login", "Signup"]
    )

    # SIGNUP

    if choice == "Signup":

        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Signup"):

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO users(username,email,password)
                VALUES(?,?,?)
                """,
                (username,email,password)
            )

            conn.commit()
            conn.close()

            st.success("Account Created Successfully")

    # LOGIN

    if choice == "Login":

        email = st.text_input("Email")

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            conn = connect_db()

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM users
                WHERE email=? AND password=?
                """,
                (email,password)
            )

            user = cursor.fetchone()

            conn.close()

            if user:

                st.session_state.logged_in = True
                st.rerun()

            else:

                st.error("Invalid credentials")

# -----------------------------------
# MAIN APP
# -----------------------------------

else:

    st.markdown(
        '<div class="logo">✨ Curatrix</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Discover Fashion Smarter</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Home"):
            st.session_state.page = "home"
            st.rerun()

    with col2:
        if st.button(f"Cart ({len(st.session_state.cart)})"):
            st.session_state.page = "cart"
            st.rerun()

    with col3:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.cart = []
            st.rerun()

    st.markdown("---")

    # -----------------------------------
    # HOME PAGE
    # -----------------------------------

    if st.session_state.page == "home":

        search = st.text_input(
            "",
            placeholder="Search Nike, Adidas, Puma..."
        )

        cols = st.columns(4, gap="large")

        filtered_products = []

        for product in products:

            if search.lower() in product["name"].lower():

                filtered_products.append(product)

        for index, product in enumerate(filtered_products):

            with cols[index % 4]:

                st.markdown(
                    '<div class="product-card">',
                    unsafe_allow_html=True
                )

                st.image(
                    product["image"],
                    use_container_width=True
                )

                # CLICK PRODUCT

                if st.button(
                    product["name"],
                    key=f"view_{product['name']}"
                ):

                    st.session_state.selected_product = (
                        product["name"]
                    )

                    st.rerun()

                st.markdown(
                    f"""
                    <div class="brand">
                        {product['brand']}
                    </div>

                    <div class="price">
                        ₹{product['price']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # ADD TO CART

                if st.button(
                    "Add to Cart",
                    key=f"cart_{product['name']}"
                ):

                    st.session_state.cart.append(product)

                    st.success(
                        f"{product['name']} added to cart"
                    )

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

                # PRODUCT DETAILS

                if (
                    st.session_state.selected_product
                    == product["name"]
                ):

                    st.markdown(
                        "## ✨ AI Style Suggestions"
                    )

                    recommendation = (
                        get_fashion_recommendation(
                            product["name"]
                        )
                    )

                    for item in recommendation:

                        st.success(item)

                    st.markdown(
                        "## 💰 Price Comparison"
                    )

                    if (
                        product["name"]
                        in price_comparison
                    ):

                        prices = price_comparison[
                            product["name"]
                        ]

                        lowest_price = min(
                            prices.values()
                        )

                        for site, price in prices.items():

                            if price == lowest_price:

                                st.success(
                                    f"{site}: ₹{price} ✅ Best Deal"
                                )

                            else:

                                st.write(
                                    f"{site}: ₹{price}"
                                )

                            if site in website_links:

                                st.markdown(
                                    f"[Open {site}]({website_links[site]})"
                                )

                    else:

                        st.warning(
                            "Comparison not available yet"
                        )

    # -----------------------------------
    # CART PAGE
    # -----------------------------------

    if st.session_state.page == "cart":

        st.markdown(
            '<div class="heading">Your Cart</div>',
            unsafe_allow_html=True
        )

        total = 0

        if len(st.session_state.cart) == 0:

            st.write("Your cart is empty")

        else:

            for index, item in enumerate(st.session_state.cart):

                col1, col2 = st.columns([1,2])

                with col1:

                    st.image(
                        item["image"],
                        width=220
                    )

                with col2:

                    st.markdown(
                        f"""
                        <div class="brand">
                            {item['brand']}
                        </div>

                        <div class="product-title">
                            {item['name']}
                        </div>

                        <div class="price">
                            ₹{item['price']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    total += item["price"]

                    if st.button(
                        "Remove Item",
                        key=f"remove{index}"
                    ):

                        st.session_state.cart.pop(index)
                        st.rerun()

            st.markdown("---")

            st.subheader(
                f"Total Amount: ₹{total}"
            )

            # CHECKOUT BUTTON

            if st.button("Proceed to Checkout"):

                st.session_state.page = "checkout"
                st.rerun()

    # -----------------------------------
    # CHECKOUT PAGE
    # -----------------------------------

    if st.session_state.page == "checkout":

        st.markdown(
            '<div class="heading">Checkout</div>',
            unsafe_allow_html=True
        )

        st.text_input("Full Name")

        st.text_input("Card Number")

        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Expiry Date")

        with col2:
            st.text_input(
                "CVV",
                type="password"
            )

        st.text_area("Billing Address")

        st.selectbox(
            "Payment Method",
            [
                "Credit Card",
                "Debit Card",
                "UPI",
                "Cash on Delivery"
            ]
        )

        total = 0

        for item in st.session_state.cart:
            total += item["price"]

        st.markdown("---")

        st.subheader(
            f"Total Payable: ₹{total}"
        )

        if st.button("Place Order"):

            st.session_state.page = "success"

            st.session_state.cart = []

            st.rerun()

    # -----------------------------------
    # SUCCESS PAGE
    # -----------------------------------

    if st.session_state.page == "success":

        st.balloons()

        st.markdown(
            '''
            <div style="
            text-align:center;
            padding:40px;
            ">

            <h1 style="
            color:#F5E6D3;
            font-size:55px;
            ">
            🎉 Order Placed
            </h1>

            <p style="
            color:white;
            font-size:22px;
            ">
            Your fashion order has been placed successfully.
            </p>

            </div>
            ''',
            unsafe_allow_html=True
        )

        if st.button("Continue Shopping"):

            st.session_state.page = "home"

            st.rerun()