# Full Enhanced Customer Management System with New Features

import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px

# Initialize Session State for Login
if 'login' not in st.session_state:
    st.session_state['login'] = False
    st.session_state['user_id'] = None
    st.session_state['username'] = None
    st.session_state['user_type'] = None
    st.session_state['customer_details'] = None

# Sidebar Menu
choice = st.sidebar.selectbox("Menu", ("Home", "Dashboard", "Admin", "Customer", "Customer Login", "Customer Dashboard","Reports / Analytics" ))

# 1. Home Page
if choice == "Home":
    st.title("Customer Management System")
    st.image("https://www.itrobes.com/wp-content/uploads/2024/03/Customer-Management-System-Features.jpg")
    st.write("This is a web application developed by Pragyan Khaniya.")

# 2. Dashboard
elif choice == "Dashboard":
    st.title("\U0001F4CA Dashboard - Overview")
    db = mysql.connector.connect(host="localhost", user="root", password="password@123", database="cms")
    c = db.cursor()

    c.execute("SELECT COUNT(*) FROM customer")
    total_customers = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM products")
    total_products = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM orders")
    total_orders = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM orders WHERE order_status = 'Pending'")
    total_pending_orders = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM orders WHERE order_status = 'Completed'")
    total_completed_orders = c.fetchone()[0]
    db.close()

    col1, col2, col3 = st.columns(3)
    col1.metric("\U0001F465 Total Customers", total_customers)
    col2.metric("\U0001F4E6 Total Products", total_products)
    col3.metric("\U0001F6D2 Total Orders", total_orders)

    col4, col5 = st.columns(2)
    col4.metric("\U0001F7E2 Pending Orders", total_pending_orders)
    col5.metric("\U0001F7E3 Completed Orders", total_completed_orders)

# 3. Admin Panel
elif choice == "Admin":
    st.title("\U0001F510 Admin Panel")

    if not st.session_state['login']:
        uname = st.text_input("Enter Username")
        upass = st.text_input("Enter Password", type="password")
        btn = st.button("Login")

        if btn:
            db = mysql.connector.connect(host="localhost", user="root", password="password@123", database="cms")
            c = db.cursor(dictionary=True)
            c.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (uname, upass))
            user = c.fetchone()
            db.close()

            if user:
                st.session_state['login'] = True
                st.session_state['user_id'] = user['id']
                st.session_state['username'] = user['username']
                st.success(f"Welcome, {user['username']}!")
                st.rerun()
            else:
                st.error("Incorrect username or password")
    else:
        st.subheader(f"Welcome, {st.session_state['username']}!")
        if st.button("Logout"):
            st.session_state['login'] = False
            st.session_state['user_id'] = None
            st.session_state['username'] = None
            st.session_state['user_type'] = None
            st.session_state['customer_details'] = None
            st.rerun()

        admin_choice = st.selectbox("Manage", ("Customers", "Products", "Orders"))
        db = mysql.connector.connect(host="localhost", user="root", password="password@123", database="cms")
        c = db.cursor(dictionary=True)

        if admin_choice == "Orders":
            st.subheader("\U0001F6D2 Manage Orders")
            action = st.radio("Choose Action", ("View", "Add", "Delete", "Update Status"))

            if action == "View":
                st.write("### Order Search")
                search_name = st.text_input("Search by Customer Name")
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")

                query = """
                    SELECT o.id, o.order_date, o.order_status,
                           c.name AS customer_name, p.name AS product_name
                    FROM orders o
                    JOIN customer c ON o.customer_id = c.id
                    JOIN products p ON o.product_id = p.id
                """
                filters = []
                values = []

                if search_name:
                    filters.append("c.name LIKE %s")
                    values.append(f"%{search_name}%")
                if start_date and end_date:
                    filters.append("o.order_date BETWEEN %s AND %s")
                    values.extend([start_date, end_date])

                if filters:
                    query += " WHERE " + " AND ".join(filters)

                c.execute(query, values)
                orders = c.fetchall()
                st.table(orders)

            elif action == "Add":
                customer_id = st.number_input("Enter Customer ID", min_value=1)
                c.execute("SELECT id, name FROM products")
                products = c.fetchall()
                product_options = {p['id']: p['name'] for p in products}
                product_choice = st.selectbox("Choose Product", product_options.values())
                product_id = [k for k, v in product_options.items() if v == product_choice][0]
                order_date = st.date_input("Enter Order Date")
                order_status = st.selectbox("Order Status", ("Pending", "Completed"))
                if st.button("Add Order"):
                    c.execute("INSERT INTO orders (customer_id, order_date, order_status, product_id) VALUES (%s, %s, %s, %s)",
                              (customer_id, order_date, order_status, product_id))
                    db.commit()
                    st.success("Order Added Successfully!")
                    st.rerun()

            elif action == "Delete":
                order_id_del = st.number_input("Enter Order ID", min_value=1)
                if st.button("Delete Order"):
                    c.execute("DELETE FROM orders WHERE id=%s", (order_id_del,))
                    db.commit()
                    st.warning("Order Deleted!")
                    st.rerun()

            elif action == "Update Status":
                order_id = st.number_input("Enter Order ID to Update", min_value=1)
                new_status = st.selectbox("New Status", ["Pending", "Completed"])
                if st.button("Update Status"):
                    c.execute("UPDATE orders SET order_status = %s WHERE id = %s", (new_status, order_id))
                    db.commit()
                    st.success("Order status updated.")
                    st.rerun()

        elif admin_choice == "Customers":
            st.subheader("\U0001F465 Manage Customers")
            action = st.radio("Choose Action", ("View", "Add", "Delete"))
            if action == "View":
                c.execute("SELECT * FROM customer")
                st.table(c.fetchall())
            elif action == "Add":
                name = st.text_input("Customer Name")
                address = st.text_input("Customer Address")
                phone = st.text_input("Customer Phone")
                if st.button("Add Customer"):
                    c.execute("INSERT INTO customer (name, address, phone) VALUES (%s, %s, %s)", (name, address, phone))
                    db.commit()
                    st.success("Customer Added Successfully!")
                    st.rerun()
            elif action == "Delete":
                customer_id = st.number_input("Enter Customer ID", min_value=1)
                if st.button("Delete Customer"):
                    c.execute("DELETE FROM customer WHERE id=%s", (customer_id,))
                    db.commit()
                    st.warning("Customer Deleted!")
                    st.rerun()

        elif admin_choice == "Products":
            st.subheader("\U0001F4E6 Manage Products")
            action = st.radio("Choose Action", ("View", "Add", "Delete"))
            if action == "View":
                c.execute("SELECT * FROM products")
                st.table(c.fetchall())
            elif action == "Add":
                name = st.text_input("Product Name")
                price = st.number_input("Product Price", min_value=0.01)
                if st.button("Add Product"):
                    c.execute("INSERT INTO products (name, price) VALUES (%s, %s)", (name, price))
                    db.commit()
                    st.success("Product Added Successfully!")
                    st.rerun()
            elif action == "Delete":
                product_id = st.number_input("Enter Product ID", min_value=1)
                if st.button("Delete Product"):
                    c.execute("DELETE FROM products WHERE id=%s", (product_id,))
                    db.commit()
                    st.warning("Product Deleted!")
                    st.rerun()
        db.close()

# 4. Customer Registration
elif choice == "Customer":
    st.title("\U0001F4DD Customer Registration")
    name = st.text_input("Full Name")
    address = st.text_input("Address")
    phone = st.text_input("Phone Number")
    uname = st.text_input("Username")
    upass = st.text_input("Password", type="password")
    if st.button("Register"):
        if name and address and phone and uname and upass:
            db = mysql.connector.connect(host="localhost", user="root", password="password@123", database="cms")
            c = db.cursor()
            try:
                c.execute("INSERT INTO customer (name, address, phone, username, password) VALUES (%s, %s, %s, %s, %s)",
                          (name, address, phone, uname, upass))
                db.commit()
                st.success("\u2705 Registration Successful!")
            except mysql.connector.Error as e:
                st.error(f"\u274C Error: {e}")
            db.close()

# 5. Customer Login
elif choice == "Customer Login":
    st.title("\U0001F511 Customer Login")
    if not st.session_state['login'] or st.session_state['user_type'] != "customer":
        uname = st.text_input("Enter Username")
        upass = st.text_input("Enter Password", type="password")
        btn = st.button("Login")
        if btn:
            db = mysql.connector.connect(host="localhost", user="root", password="password@123", database="cms")
            c = db.cursor(dictionary=True)
            c.execute("SELECT * FROM customer WHERE username=%s AND password=%s", (uname, upass))
            user = c.fetchone()
            db.close()
            if user:
                st.session_state['login'] = True
                st.session_state['user_id'] = user['id']
                st.session_state['username'] = user['username']
                st.session_state['user_type'] = "customer"
                st.session_state['customer_details'] = user
                st.success(f"Welcome, {user['username']}!")
                st.rerun()
            else:
                st.error("Incorrect username or password")
    else:
        st.subheader(f"Welcome, {st.session_state['username']}!")
        if st.button("Logout"):
            st.session_state['login'] = False
            st.session_state['user_id'] = None
            st.session_state['username'] = None
            st.session_state['user_type'] = None
            st.session_state['customer_details'] = None
            st.rerun()

# 6. Customer Dashboard
elif choice == "Customer Dashboard":
    if not st.session_state['login'] or st.session_state['user_type'] != "customer":
        st.error("You need to login first!")
    else:
        st.title("\U0001F4CB Customer Dashboard")
        st.subheader("Your Details")
        customer_details = st.session_state.get('customer_details', {})
        st.write(f"**Name:** {customer_details.get('name', 'N/A')}")
        st.write(f"**Address:** {customer_details.get('address', 'N/A')}")
        st.write(f"**Phone:** {customer_details.get('phone', 'N/A')}")

        db = mysql.connector.connect(host="localhost", user="root", password="password@123", database="cms")
        c = db.cursor(dictionary=True)

        st.subheader("Your Orders")
        c.execute("SELECT o.id, o.order_date, o.order_status, p.name AS product_name FROM orders o JOIN products p ON o.product_id = p.id WHERE o.customer_id = %s", (st.session_state['user_id'],))
        orders = c.fetchall()
        st.table(orders)

        # Order count
        c.execute("SELECT COUNT(*) FROM orders WHERE customer_id = %s", (st.session_state['user_id'],))
        order_count = c.fetchone()['COUNT(*)']
        st.metric("\U0001F4E6 Total Orders", order_count)

        # Download CSV
        if orders:
            df_orders = pd.DataFrame(orders)
            csv = df_orders.to_csv(index=False).encode('utf-8')
            st.download_button("\U0001F4E5 Download Order History", data=csv, file_name="order_history.csv", mime="text/csv")

        st.subheader("Place a New Order")
        c.execute("SELECT id, name FROM products")
        products = c.fetchall()
        product_options = {p['id']: p['name'] for p in products}
        product_choice = st.selectbox("Choose Product", product_options.values())
        product_id = [k for k, v in product_options.items() if v == product_choice][0]

        order_date = st.date_input("Order Date")
        order_status = st.selectbox("Order Status", ("Pending", "Completed"))

        if st.button("Place Order"):
            c.execute("INSERT INTO orders (customer_id, order_date, order_status, product_id) VALUES (%s, %s, %s, %s)",
                      (st.session_state['user_id'], order_date, order_status, product_id))
            db.commit()
            st.success("\u2705 Order Placed Successfully!")
            st.rerun()

        st.subheader("\U0001F4AC Submit Feedback")
        feedback_text = st.text_area("Write your feedback here")
        feedback_rating = st.slider("Rate your experience (1-5 stars)", 1, 5, 3)
        if st.button("Submit Feedback"):
            c.execute("INSERT INTO feedback (customer_id, message, rating) VALUES (%s, %s, %s)",
                      (st.session_state['user_id'], feedback_text, feedback_rating))
            db.commit()
            st.success("\U0001F44D Feedback submitted. Thank you!")

        db.close()
elif choice == "Reports / Analytics":
    st.title("📊 Reports & Order Trends")
    db = mysql.connector.connect(
        host="localhost", user="root", password="password@123", database="cms"
    )
    c = db.cursor()

    # --- 1. Daily Order Trends
    c.execute("""
        SELECT order_date, COUNT(*) as order_count
        FROM orders
        GROUP BY order_date
        ORDER BY order_date
    """)
    data = c.fetchall()
    df_daily = pd.DataFrame(data, columns=["Date", "Order Count"])
    if not df_daily.empty:
        fig1 = px.line(df_daily, x="Date", y="Order Count", title="📅 Daily Order Trends")
        st.plotly_chart(fig1)
    else:
        st.info("No order data found.")

    # --- 2. Orders by Status
    c.execute("""
        SELECT order_status, COUNT(*) FROM orders
        GROUP BY order_status
    """)
    status_data = c.fetchall()
    df_status = pd.DataFrame(status_data, columns=["Status", "Count"])
    if not df_status.empty:
        fig2 = px.pie(df_status, names="Status", values="Count", title="🧾 Order Status Distribution")
        st.plotly_chart(fig2)

    # --- 3. Orders by Product
    c.execute("""
        SELECT p.name, COUNT(*) as order_count
        FROM orders o
        JOIN products p ON o.product_id = p.id
        GROUP BY p.name
        ORDER BY order_count DESC
    """)
    product_data = c.fetchall()
    df_product = pd.DataFrame(product_data, columns=["Product", "Order Count"])
    if not df_product.empty:
        fig3 = px.bar(df_product, x="Product", y="Order Count", title="📦 Orders by Product")
        st.plotly_chart(fig3)

    db.close()

