import streamlit as st
import os
from products import products
from utils import get_filtered_products, show_cart
from checkout import show_checkout_form
from auth import show_login, show_profile

# Initialize session states
def initialize_session_states():
    session_defaults = {
        "authenticated": False,
        "cart": [],
        "wishlist": [],
        "current_page": "Home",
        "selected_product": None,
        "dark_mode": False,
        "user": {
            "name": "",
            "email": ""
        },
    }

    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_states()

# Sidebar navigation
import os

logo_path = os.path.join(os.path.dirname(__file__), "images", "logo.jpg")

if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=200)
else:
    st.sidebar.error("❌ File logo tidak ditemukan!")

def setup_sidebar():
    st.sidebar.header("Menu")
    pages = ["🏡 Home", "🗂️ Products Details", "❤️ Wishlist", "🛒 Cart", "🛍️ Checkout", "🔑 Login"]
    st.session_state.current_page = st.sidebar.radio("Go to", pages) 
    show_profile() 

# Handle authentication
def check_authentication():
    if not st.session_state.authenticated and st.session_state.current_page != "🔑 Login":
        show_login()
        st.stop()

# Products Filtering and Sorting
def get_product_filters(): 
    category_filter = st.sidebar.selectbox(
        "📂 Filter by Category",
        ["All"] + list(set(p["category"] for p in products))
    )
    sort_option = st.sidebar.selectbox(
        "🔽 Sort by",
        ["Price: Low to High", "Price: High to Low", "Rating", "Newest"]
    )
    return category_filter, sort_option

def sort_products(products, sort_option):
    if sort_option == "Price: Low to High":
        return sorted(products, key=lambda x: x["price"])
    elif sort_option == "Price: High to Low":
        return sorted(products, key=lambda x: x["price"], reverse=True)
    elif sort_option == "Rating":
        return sorted(products, key=lambda x: x.get("rating", 0), reverse=True)
    return products 

# Product Display
def display_products_card(product, col):
    with col:
        st.image(product.get("image", "https://via.placeholder.com/150"), width=150)
        st.subheader(product["name"])
        st.write(f"Price: Rp{product['price']:.2f}")
        st.write(f"⭐ {product.get('rating', 'No rating')} / 5")

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"📄 Details - {product['name']}", key=f"details_{product['name']}"):
                st.session_state.selected_product = product
                st.session_state.current_page = "🗂️ Products Details"
                st.rerun()
        with col2:
            if st.button(f"🛒 Add - {product['name']}", key=f"add_{product['name']}"):
                st.session_state.cart.append(product)
                st.success(f"{product['name']} Added to cart!")

def get_filtered_products(products, category_filter, min_price, max_price):
    filtered = [p for p in products if
                (category_filter == "All" or p["category"] == category_filter)
                and min_price <= p["price"] <= max_price]
    return filtered
        
def show_products():
    st.header("🛍️ Products")
    category_filter, sort_option = get_product_filters()

    filtered_products = get_filtered_products(
        products,category_filter, 0, float("inf")
    )
    sorted_products = sort_products(filtered_products, sort_option)

    cols = st.columns(3)
    for idx, product in enumerate(sorted_products):
        display_products_card(product, cols[idx % 3])

# Product details
def show_product_details():
    product = st.session_state.selected_product
    if not product:
        st.error("No product selected.")
        return
    
    st.image(product.get("image", "https://via.placeholder.com/300"), width=300)
    st.subheader(product["name"])
    st.write(f"Price: Rp{product['price']:.2f}")
    st.write(f"📂 Category: {product['category']}")
    st.write(f"⭐ Rating {product.get('rating', 'No rating')} / 5")
    st.write(product.get("description", "No description available."))

    if "features" in product:
        st.subheader("🔹 Features:")
        for feature in product["features"]:
            st.write(f"- {feature}")
    
    if "specs" in product:
        st.subheader("🔧 Specifications")
        for key, value in product["specs"].items():
            st.write(f"**{key}:**{value}")

    if "reviews" in product:
        st.subheader("📄 Reviews")
        for review in product["reviews"]:
            st.write(f"**{review['user']}** ({review['rating']}/5): {review['comment']}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛒 Add to Card"):
            st.session_state.cart.append(product)
            st.success(f"{product['name']} added to cart!")
    with col2:
        if st.button("❤️ Add to Wishlist"):
            st.session_state.wishlist.append(product)
            st.success(f"{product['name']} added to wishlist!")

# Wishlist
def show_wishlist():
    st.header("❤️ Wishlist")
    if not st.session_state.wishlist:
        st.write("Your wishlist is empty.")
        return
    
    for item in st.session_state.wishlist:
        st.write(f"- {item['name']} - Rp{item['price']:.2f}")
        if st.button(f"🛒 Move to Cart - {item['name']}", key=f"wishlist_{item['name']}"):
            st.session_state.cart.append(item)
            st.session_state.wishlist.remove(item)
            st.success(f"{item['name']} moved to cart!")
            st.rerun()

# Cart
def show_cart():
    st.header("🛒 Cart")
    if not st.session_state.cart:
        st.write("Your cart is empty.")
        return
    
    total_price = sum(p["price"] for p in st.session_state.cart)
    for item in st.session_state.cart:
        st.image(item.get("image", "https://via.placeholder.com.100"), width=100)
        st.write(f"- {item['name']} - Rp{item['price']:.2f}")
        if st.button(f"❌ Remove {item['name']}", key=f"remove_{item['name']}"):
            st.session_state.cart.remove(item)
            st.rerun()

    total_price = sum(p["price"] for p in st.session_state.cart)
    st.write(f"**Total: Rp{total_price:.2f}**")
    if st.button("📂 Proceed to Checkout"):
        st.session_state.current_page = "📂 Checkout"
        st.rerun()

# Checkout
def show_checkout():
    st.header("📂 Checkout")
    if not st.session_state.cart:
        st.write("Your cart is empty. Add products before checking out!")
        return
    show_checkout_form()

# Main functions to run the app
def main():
    st.title("Chili Mate 🌶️")
    setup_sidebar()
    check_authentication()

# if len(products):
# st.header("Products")
# for product in products:
# st.write(f"**{product['name']}**")
# else:
# st.info("No products available.")
        
    page_handlers = {
        "🏡 Home": show_products,
        "🗂️ Products Details": show_product_details,
        "🛒 Cart": show_cart,
        "❤️ Wishlist": show_wishlist,
        "🛍️ Checkout": show_checkout,
        "🔑 Login": show_login
    }

    page_handlers[st.session_state.current_page]()
    
if __name__ == "__main__":
    main()

def display_products_card(product, col):
    with col:
        # Card container with hover effect
        with st.container():
           # Image with fixed aspect ratio
           st.image(
               product.get("image", "https://via.placeholder.com/300"),
               use_column_width=True,
               output_format="auto"   
            )
           
           # Product name and category
           st.markdown(f"**{product['name']}**")
           st.caption(f"📂 {product['category']}")
           
    # Price and discount
    original_price = product.get("original_price", product["price"])
    if original_price != product["price"]:
        st.markdown(f"""
            <span style="text-decoration: line-through; color: red;">Rp{original_price:.2f}</span>
            <span style="color: green;">Rp{product['price']:.2f}</span>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"**Rp{product['price']:.2f}**")

        # Rating with stars
        rating = product.get("rating", 0)
        stars = "⭐" * int(rating) + "☆" * (5 - int(rating))
        st.markdown(f"{stars} ({rating}/5)")    

        # Quick actions
        col1, col2 = st.columns([1, 1])    
        with col1:
            if st.button(f"📄 Details", key=f"details_{product['id']}"):
                st.session_state.selected_product = product
                st.session_state.current_page = "🗂️ Products Details"
                st.rerun()     
            with col2:  
                if st.button(f"🛒 Add to Cart", key=f"add_{product['id']}"):
                    st.session_state.cart.append(product)
                    st.success(f"{product['name']} added to cart!")

            # Additional info
            with st.expander("More Info"):
               if "features" in product:
                   st.write("**🔹 Features:**")
                   for feature in product["features"]:
                       st.write(f"- {feature}")
               if "specs" in product:
                    st.write("**🔧 Specifications:**")
                    for key, value in product["specs"].items():
                        st.write(f"**{key}:** {value}")

def show_products():
    st.header("🛍️ Products")

# Apply filters and sorting
def get_product_filters():
    category_filter = st.sidebar.selectbox(
        "📂 Filter by Category",
        ["All"] + list(set(p["category"] for p in products))
    )
    sort_option = st.sidebar.selectbox(
        "🔽 Sort by",
        ["Price: Low to High", "Price: High to Low", "Rating", "Newest"]
    )
    return category_filter, sort_option


    # Responsive grid layout
    cols = st.columns(3)
    for idx, product in enumerate(sorted_products):
        display_products_card(product, cols[idx % 3])

        # Create new row after every 3 products
        if (idx + 1) % 3 == 0 and (idx + 1) < len(sorted_products):
            cols = st.columns(3)





               
               
