import pandas as pd
import psycopg2
import streamlit as st
from configparser import ConfigParser

"### Electronic commerce information search system"


@st.cache
def get_config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}


@st.cache
def query_db(sql: str):
    #print(f"Running query_db(): {sql}")

    db_info = get_config()

    # Connect to an existing database
    conn = psycopg2.connect(**db_info)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    try:
        cur.execute(sql)
    except psycopg2.Error as e:
        print(f"error: {e}")


    # Obtain data
    data = cur.fetchall()

    column_names = [desc[0] for desc in cur.description]

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

    df = pd.DataFrame(data=data, columns=column_names)

    return df

with st.expander("All tables information"):
    "### All Tables"
    sql_all_table_names = "SELECT relname FROM pg_class WHERE relkind='r' AND relname !~ '^(pg_|sql_)';"
    try:
        all_table_names = query_db(sql_all_table_names)["relname"].tolist()
        table_name = st.selectbox("Choose a table", all_table_names)
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")

    if table_name:
        f"Display the table"

        sql_table = f"SELECT * FROM {table_name};"
        try:
            df = query_db(sql_table)
            st.dataframe(df)
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again."
            )

with st.expander("Customer information"):
    "### Customer Information"
    sql_customer_names = "SELECT name FROM customers;"
    try:
        customer_names = query_db(sql_customer_names)["name"].tolist()
        customer_name = st.selectbox("Choose a customer", customer_names)
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")

    if customer_name:
        sql_customer = f"SELECT * FROM customers WHERE name = '{customer_name}';"
        try:
            df = query_db(sql_customer)
            st.table(df)
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again."
            )
    
    "### Customer Order History"
    sql_customer_cids = "SELECT cid FROM customers;"
    try:
        customer_cids = query_db(sql_customer_cids)["cid"].tolist()
        customer_cid = st.selectbox("Input a customer id", customer_cids, key = "order_history")
    except:
        st.write("Sorry! Something went wrong with your query, please try again.1")

    if customer_cid:
        sql_customer_order = f"""SELECT OP.order_id, P.name, OPS.quantity,to_char(OPS.total_amount,'999999.99') as total_amount,OPS.order_date,CAST(OPS.order_time AS varchar),OPS.description
                                 FROM Orders_Placed_Shipped as OPS, O_contain_P as OP, Products as P
                                 WHERE OPS.cid = {customer_cid}
                                 AND OPS.order_id = OP.order_id
                                 And OP.pid = P.pid;"""
        try:
            df = query_db(sql_customer_order)
            st.table(df)
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again.2"
            )

    "### Customer Review History"
    sql_customer_cids = "SELECT cid FROM customers;"
    try:
        customer_cids = query_db(sql_customer_cids)["cid"].tolist()
        customer_cid = st.selectbox("Input a customer id", customer_cids,key = "review_history")
    except:
        st.write("Sorry! Something went wrong with your query, please try again.1")

    if customer_cid:
         sql_customer_reviews = f"""SELECT RRW.review_date, CAST(RRW.review_time AS varchar), P.name as product_name, RRW.score, RRW.review_text
                                  FROM Reviews_Reviewed_Written as RRW, Products as P
                                  WHERE RRW.cid = {customer_cid}
                                  AND RRW.pid = P.pid;"""
         try:
            df = query_db(sql_customer_reviews)
            st.table(df)
         except:
            st.write(
                 "Sorry! Something went wrong with your query, please try again.2"
             )

    "### Customer's Favorite Product Category And Manufacturer Based On The Purchase History"
    sql_customer_ids = "SELECT cid FROM Customers;"
    try:
        customer_ids = query_db(sql_customer_ids)["cid"].tolist()
        customer_id = st.selectbox("Choose a customer", customer_ids)
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")
    
    if customer_id:
        sql_query1 = f"SELECT PC.category, COUNT(*) as count\
                      FROM Orders_Placed_Shipped OPS, O_Contain_P OP, P_BelongTo_C PC \
                      WHERE OPS.cid = '{customer_id}' \
                      AND OPS.order_id = OP.order_id \
                      AND OP.pid = PC.pid \
                      GROUP BY PC.category \
                      ORDER BY count DESC LIMIT 1"
        sql_query2 = f"SELECT MP.manufacture_name, MP.manufacture_city, COUNT(*) as count\
                      FROM Orders_Placed_Shipped OPS, O_Contain_P OP, M_Make_P MP \
                      WHERE OPS.cid = '{customer_id}' \
                      AND OPS.order_id = OP.order_id \
                      AND OP.pid = MP.pid \
                      GROUP BY MP.manufacture_name, MP.manufacture_city \
                      ORDER BY count DESC LIMIT 1"
        
        try:
            info = query_db(sql_query1).loc[0]
            category = (info["category"])
            
            info = query_db(sql_query2).loc[0]
            manufacture_name, manufacture_city = (info["manufacture_name"], info["manufacture_city"])
            
            st.write(f"Favorite Product Category: {category}")
            st.write(f"Favorite Manufacturer Name & City: {manufacture_name} : {manufacture_city}")
        except:
            st.write(
                "Sorry! Something went wrong with your query1 or 2, please try again."
            )
     
           

with st.expander("Order information"):
    "### Order Information"
    sql_order_ids = "SELECT order_id FROM orders_placed_shipped;"
    try:
        order_ids = query_db(sql_order_ids)["order_id"].tolist()
        order_id = st.selectbox("Choose an order", order_ids)
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")

    if order_id:
        sql_order = f"""
            SELECT C.name, O.order_date, O.quantity, to_char(O.total_amount,'999999.99') as total_amount, O.description
            FROM orders_placed_shipped as O, customers as C 
            WHERE O.order_id = {order_id}
            AND O.cid = C.cid;"""

        try:
            df = query_db(sql_order)
            st.table(df)
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again."
            )


with st.expander("Product information"):
    "### Product information"
    sql_product_ids = "SELECT pid FROM products;"
    try:
        product_ids = query_db(sql_product_ids)["pid"].tolist()
        product_id = st.selectbox("Choose an product id", product_ids, key="product_information")
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")

    if product_id:
        sql_product = f"""
            SELECT p.name,to_char(p.price,'999999.99') as price,p.in_stock,p.brand,p.description
            FROM products as P
            WHERE pid = {product_id}"""

        try:
            df = query_db(sql_product)
            st.table(df)
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again."
            )

    "### Product Reviews"
    sql_product_ids = "SELECT pid FROM products;"
    try:
        product_ids = query_db(sql_product_ids)["pid"].tolist()
        product_id = st.selectbox("Choose an product id", product_ids, key="product_reviews")
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")

    if product_id:
        sql_product_review1 = f"""
            Select P.pid, COUNT(RRW.score) as one_star
            FROM Products P, Reviews_Reviewed_Written RRW
            WHERE P.pid = {product_id}
            AND P.pid = RRW.pid
            AND RRW.score = 1
            GROUP BY P.pid;"""

        sql_product_review2 = f"""
            Select P.pid, COUNT(RRW.score) as two_star
            FROM Products P, Reviews_Reviewed_Written RRW
            WHERE P.pid = {product_id}
            AND P.pid = RRW.pid
            AND RRW.score = 2
            GROUP BY P.pid;"""

        sql_product_review3 = f"""
            Select P.pid, COUNT(RRW.score) as three_star
            FROM Products P, Reviews_Reviewed_Written RRW
            WHERE P.pid = {product_id}
            AND P.pid = RRW.pid
            AND RRW.score = 3
            GROUP BY P.pid;"""

        sql_product_review4 = f"""
            Select P.pid, COUNT(RRW.score) as four_star
            FROM Products P, Reviews_Reviewed_Written RRW
            WHERE P.pid = {product_id}
            AND P.pid = RRW.pid
            AND RRW.score = 4
            GROUP BY P.pid;"""

        sql_product_review5 = f"""
            Select P.pid, COUNT(RRW.score) as five_star
            FROM Products P, Reviews_Reviewed_Written RRW
            WHERE P.pid = {product_id}
            AND P.pid = RRW.pid
            AND RRW.score = 5
            GROUP BY P.pid;"""

        try:
            df1 = query_db(sql_product_review1)
            df2 = query_db(sql_product_review2)
            df3 = query_db(sql_product_review3)
            df4 = query_db(sql_product_review4)
            df5 = query_db(sql_product_review5)

            df1_copy = df1.copy(deep=True)
            df2_copy = df2.copy(deep=True)
            df3_copy = df3.copy(deep=True)
            df4_copy = df4.copy(deep=True)
            df5_copy = df5.copy(deep=True)

            if df1_copy.empty:
                df1_copy.loc[0] = ["None",0]
            if df2_copy.empty:
                df2_copy.loc[0] = ["None",0]
            if df3_copy.empty:
                df3_copy.loc[0] = ["None",0]
            if df4_copy.empty:
                df4_copy.loc[0] = ["None",0]
            if df5_copy.empty:
                df5_copy.loc[0] = ["None",0]

            result = pd.concat([df1_copy[['one_star']],df2_copy[['two_star']],df3_copy[['three_star']],df4_copy[['four_star']],df5_copy[['five_star']]],axis=1)

            st.dataframe(result)
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again."
            )

    "### Product Manufactures And Categories"
    sql_product_ids = "SELECT pid FROM Products;"
    try:
        product_ids = query_db(sql_product_ids)["pid"].tolist()
        product_id = st.selectbox("Choose a product id", product_ids)
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")
            
    if product_id:
        sql_query1 = f"SELECT * FROM M_Make_P WHERE pid = '{product_id}';"
        sql_query2 = f"SELECT * FROM P_BelongTo_C WHERE pid = '{product_id}';"
        
        try:
            manufacture_info = query_db(sql_query1).loc[0]
            manufacture_name, manufacture_city = (
                manufacture_info["manufacture_name"],
                manufacture_info["manufacture_city"]
            )
            category_info = query_db(sql_query2).loc[0]
            category_name = (
                category_info["category"]
            )
            st.write(f"Manufacture Name: {manufacture_name}")
            st.write(f"Manufacture City: {manufacture_city}")
            st.write(f"Category Name: {category_name}")

        except:
            st.write(
                "Sorry! Something went wrong with your query2, please try again."
            )

    "### Product Review Scores"
    sql_product_names = "SELECT name FROM Products;"
    try:
        product_names = query_db(sql_product_names)["name"].tolist()
        product_name = st.selectbox("Choose a product name", product_names)
    except:
        st.write("Sorry! Something went wrong with your query! Please try again.")
        
    if product_name:
        product_name = product_name.replace("'", "''")
        sql_query = f"SELECT ROUND(AVG(R.score), 2) as average, MAX(R.score) as maximum, MIN(R.score) as minimum, COUNT(*) as total\
                        FROM Reviews_Reviewed_Written R, Products P \
                        WHERE R.pid = P.pid \
                        GROUP BY P.pid \
                        HAVING P.name = '{product_name}';"
        try:
            df = query_db(sql_query)
            st.table(df)
        except:
            st.write(
                "Sorry! Something went wrong with your query2, please try again."
            )

    "### Product With Highest Score In Category"
    sql_category_names = "SELECT name FROM Categories"
    try:
        category_names = query_db(sql_category_names)["name"].tolist()
        category_name = st.selectbox("Choose a product category", category_names)
    except:
        st.write("Sorry! Something went wrong with your query! Please try again.")
        
    if category_name:
        sql_query = f"""SELECT P.name, R.score 
                      FROM P_BelongTo_C PC, Products P, Reviews_Reviewed_Written R
                      WHERE PC.pid = P.pid 
                      AND P.pid = R.pid
                      AND PC.category = '{category_name}'
                      AND R.score = (Select MAX(R.score) FROM P_BelongTo_C PC, Products P, Reviews_Reviewed_Written R
                      WHERE PC.pid = P.pid 
                      AND P.pid = R.pid
                      AND PC.category = '{category_name}'
);"""
    
        try:
            df = query_db(sql_query)
            st.table(df)
        except:
            st.write(
                "Sorry! We don't have products in our database with such chosen category!"
            )
     

with st.expander("Shipment information"):
    "### Shipment Information"
    sql_shipment_ids = "SELECT sid FROM shipments;"
    try:
        shipment_ids = query_db(sql_shipment_ids)["sid"].tolist()
        shipment_id = st.selectbox("Choose a shipment id", shipment_ids)
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")

    if shipment_id:
        sql_shipment = f"""
            SELECT *
            FROM shipments as S
            WHERE sid = {shipment_id}"""

        try:
            df = query_db(sql_shipment)
            st.table(df)
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again."
            )

    "### Oder Shipment Information"
    sql_order_ids = "SELECT order_id FROM Orders_Placed_Shipped;"
    try:
        order_ids = query_db(sql_order_ids)["order_id"].tolist()
        order_id = st.selectbox("Choose an order id", order_ids)
    except:
        st.write("Sorry! Something went wrong with your query1, please try again.")
        
    if order_id:
        sql_shipment = f"SELECT S.type,S.origin_city,S.destination_city,S.company FROM Shipments S, Orders_Placed_Shipped OPS \
                        WHERE S.sid = OPS.sid \
                        AND order_id = '{order_id}';"
        try:
            df = query_db(sql_shipment)
            st.table(df)
        except:
            st.write(
                "Sorry! Something went wrong with your query2, please try again."
            )
