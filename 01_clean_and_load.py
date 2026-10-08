import os
import pandas as pd
from sqlalchemy import create_engine

try:
    import pymysql
except ImportError:
    pymysql = None

DB_NAME = "cart2insights"
RAW_PATH = "data/raw"
CLEAN_PATH = "data/cleaned"
SQLITE_DB_PATH = os.path.abspath(os.path.join("data", "cart2insights.db"))
os.makedirs(CLEAN_PATH, exist_ok=True)

# 1. Get MySQL credentials when available; fall back to SQLite if MySQL is not installed
mysql_password = os.getenv("MYSQL_ROOT_PASSWORD")
if mysql_password is None:
    try:
        mysql_password = input("Enter your MySQL root password (press Enter to use SQLite fallback): ")
    except EOFError:
        mysql_password = ""


def build_engine():
    if pymysql is None:
        print("⚠️ MySQL client not installed. Falling back to SQLite.")
        return create_engine(f"sqlite:///{SQLITE_DB_PATH}"), "sqlite"

    try:
        conn = pymysql.connect(host='localhost', user='root', password=mysql_password, connect_timeout=5)
        conn.close()
        engine = create_engine(f"mysql+pymysql://root:{mysql_password}@localhost/{DB_NAME}")
        return engine, "mysql"
    except Exception as e:
        print(f"⚠️ MySQL is unavailable ({e}). Falling back to SQLite.")
        return create_engine(f"sqlite:///{SQLITE_DB_PATH}"), "sqlite"


engine, db_type = build_engine()

if db_type == "mysql":
    try:
        conn = pymysql.connect(host='localhost', user='root', password=mysql_password)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
        conn.close()
        print(f"✅ Database '{DB_NAME}' created or already exists.")
    except Exception as e:
        print(f"❌ Error while creating MySQL database: {e}")
        raise
else:
    print(f"✅ Using SQLite database: {SQLITE_DB_PATH}")

print("\n🚀 Starting Data Cleaning & Ingestion Pipeline...")

# --- A. Load Raw Datasets ---
orders = pd.read_csv(f"{RAW_PATH}/olist_orders_dataset.csv")
customers = pd.read_csv(f"{RAW_PATH}/olist_customers_dataset.csv")
order_items = pd.read_csv(f"{RAW_PATH}/olist_order_items_dataset.csv")
payments = pd.read_csv(f"{RAW_PATH}/olist_order_payments_dataset.csv")
reviews = pd.read_csv(f"{RAW_PATH}/olist_order_reviews_dataset.csv")
products = pd.read_csv(f"{RAW_PATH}/olist_products_dataset.csv")
sellers = pd.read_csv(f"{RAW_PATH}/olist_sellers_dataset.csv")
category_translation = pd.read_csv(f"{RAW_PATH}/product_category_name_translation.csv")
geolocation = pd.read_csv(f"{RAW_PATH}/olist_geolocation_dataset.csv")

# --- B. Clean & Feature Engineer: Orders ---
date_columns = [
	'order_purchase_timestamp', 'order_approved_at', 
	'order_delivered_carrier_date', 'order_delivered_customer_date', 
	'order_estimated_delivery_date'
]
for col in date_columns:
	orders[col] = pd.to_datetime(orders[col])

# Delivery Feature Engineering: Days & Delay
orders['delivery_days'] = (orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']).dt.days
orders['delivery_delay'] = (orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']).dt.days
orders['is_delayed'] = (orders['delivery_delay'] > 0).astype(int)

# --- C. Clean & Merge Products with English Category Names ---
products = products.merge(category_translation, on='product_category_name', how='left')
products['product_category_name_english'] = products['product_category_name_english'].fillna('Other/Unknown')

# --- D. Clean Reviews ---
reviews['review_comment_title'] = reviews['review_comment_title'].fillna('No Title')
reviews['review_comment_message'] = reviews['review_comment_message'].fillna('No Comment')
reviews['review_creation_date'] = pd.to_datetime(reviews['review_creation_date'])

# --- E. Clean Geolocation (Deduplicate Zip Codes) ---
geolocation_clean = geolocation.groupby('geolocation_zip_code_prefix').agg(
	geolocation_lat=('geolocation_lat', 'mean'),
	geolocation_lng=('geolocation_lng', 'mean'),
	geolocation_city=('geolocation_city', 'first'),
	geolocation_state=('geolocation_state', 'first')
).reset_index()

# Map of tables to save & upload
datasets = {
	'orders': orders,
	'customers': customers,
	'order_items': order_items,
	'payments': payments,
	'reviews': reviews,
	'products': products,
	'sellers': sellers,
	'geolocation': geolocation_clean
}

# --- F. Upload Clean Tables to the active database & Save Clean CSVs ---
for table_name, df in datasets.items():
    # Save cleaned CSV locally
    df.to_csv(f"{CLEAN_PATH}/{table_name}_cleaned.csv", index=False)

    # Upload to the selected database backend
    df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
    print(f"📦 Table '{table_name}' cleaned, saved, and loaded into {db_type.upper()}.")

if db_type == "mysql":
    print("\n🎉 Success! All 9 datasets cleaned and uploaded to the 'cart2insights' MySQL database!")
else:
    print(f"\n🎉 Success! All 9 datasets cleaned and uploaded to the SQLite database at {SQLITE_DB_PATH}.")

