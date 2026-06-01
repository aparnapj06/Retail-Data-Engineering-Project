import pandas as pd
import os

# File path
file_path = "../Data/USECASE - Data Engineering.xlsx"

# Read sheets
product_details = pd.read_excel(file_path, sheet_name='product_details')
retail_data1 = pd.read_excel(file_path, sheet_name='retail_data1')
retail_data2 = pd.read_excel(file_path, sheet_name='retail_data2')

# Dataset information
print("\n===== DATASET SHAPES =====")
print("Product Details:", product_details.shape)
print("Retail Data1:", retail_data1.shape)
print("Retail Data2:", retail_data2.shape)

print("\n PRODUCT DETAILS COLUMNS")
print(product_details.columns.tolist())

print("\n RETAIL DATA1 COLUMNS ")
print(retail_data1.columns.tolist())

print("\n RETAIL DATA2 COLUMNS")
print(retail_data2.columns.tolist())

#MISSING VALUES
print("\n MISSING VALUES - PRODUCT DETAILS ")
print(product_details.isnull().sum())

print("\nMISSING VALUES - RETAIL DATA1")
print(retail_data1.isnull().sum())

print("\nMISSING VALUES - RETAIL DATA2 ")
print(retail_data2.isnull().sum())

#DUPLICATE ROWS
print("\n DUPLICATE ROWS")
print("Retail Data1:", retail_data1.duplicated().sum())
print("Retail Data2:", retail_data2.duplicated().sum())

# DUPLICATE TRANSACTION IDS
print("\n DUPLICATE TRANSACTION IDS ")

print(
    "Retail Data1:",
    retail_data1["transaction_id"].duplicated().sum()
)

print(
    "Retail Data2:",
    retail_data2["transaction_id"].duplicated().sum()
)

# UNIQUE PRODUCT NAMES
print("\n UNIQUE PRODUCT NAMES ")
print(sorted(retail_data1["product_name"].unique()))

print("\n UNIQUE CATEGORIES ")
print(sorted(retail_data1["category"].unique()))

print("\nPRODUCT MASTER")
print(sorted(product_details["product_name"].unique()))

print("\nCATEGORY MASTER ")
print(sorted(product_details["category"].unique()))

#Quantity Summary
print("\nQuantity Summary")

print(
    retail_data1["quantity"].describe()
)

print(
    retail_data2["quantity"].describe()
)

# Invalid Quantities
print("\nInvalid Quantities")

print(
    "Retail Data1:",
    (retail_data1["quantity"] <= 0).sum()
)

print(
    "Retail Data2:",
    (retail_data2["quantity"] <= 0).sum()
)

#Check Transaction Dates
print("\nTransaction Date Sample")
print(retail_data1["transaction_date"].head(20))

#Check Payment Method Variations
print("\nPayment Methods")
print(sorted(retail_data1["payment_method"].unique()))

#Check Payment Status
print("\nPayment Status")
print(sorted(retail_data1["payment_method"].unique()))

print(retail_data1["payment_status"].unique())

duplicate_txn = retail_data1[
    retail_data1["transaction_id"].duplicated(keep=False)
]

print(
    duplicate_txn[
        ["transaction_id", "customer_id", "product_id"]
    ]
    .sort_values("transaction_id")
    .head(20)
)


# Data Cleaning and Transformation
retail_data = pd.concat(
    [retail_data1, retail_data2],
    ignore_index=True
)

print("Total Records:", len(retail_data))

#Standardize Product Names
retail_data["product_name"] = (
    retail_data["product_name"]
    .str.strip()
    .str.title()
)

print(
    sorted(
        retail_data["product_name"].unique()
    )
)
print(
    sorted(
        product_details["product_name"].unique()
    )
)
retail_data["product_name"] = retail_data["product_name"].replace(
    {"Tv": "TV"}
)

print(
    sorted(
        retail_data["product_name"].unique()
    )
)

#Standardize Categories
print(
    sorted(
        retail_data["category"].unique()
    )
)

category_mapping = {
    "CLOTH": "Clothing",
    "clothing": "Clothing",

    "ELEC": "Electronics",
    "electronics": "Electronics",

    "FURN": "Furniture",
    "furniture": "Furniture",

    "HOME": "Home Appliances",
    "home appliances": "Home Appliances"
}

retail_data["category"] = retail_data["category"].replace(
    category_mapping
)

print(
    sorted(
        retail_data["category"].unique()
    )
)
#Check missing prices before cleaning
print(
    retail_data["price"].isnull().sum()
)

#Create a Product Price Lookup
price_lookup = product_details.set_index(
    "product_id"
)["price"]
print(price_lookup)

retail_data["price"] = retail_data["price"].fillna(
    retail_data["product_id"].map(price_lookup)
)
#Check missing prices after cleaning
print(
    retail_data["price"].isnull().sum()
)

invalid_qty = retail_data[
    retail_data["quantity"] <= 0
]

print(
    invalid_qty[
        ["transaction_id", "product_id", "quantity"]
    ].head(20)
)

#Remove invalid data
retail_data = retail_data[
    retail_data["quantity"] > 0
]
print(
    "Remaining Invalid Quantities:",
    (retail_data["quantity"] <= 0).sum()
)

print(
    "Records After Quantity Cleaning:",
    len(retail_data)
)

#remove duplicate transaction
print(
    "Duplicate Transaction IDs:",
    retail_data["transaction_id"].duplicated().sum()
)

retail_data = retail_data.drop_duplicates(
    subset=["transaction_id"],
    keep="first"
)
print(
    "Duplicate Transaction IDs After Cleaning:",
    retail_data["transaction_id"].duplicated().sum()
)

#Standardize Dates
print(
    "Records After Duplicate Removal:",
    len(retail_data)
)
retail_data["transaction_date"] = pd.to_datetime(
    retail_data["transaction_date"],
    errors="coerce"
)

retail_data["transaction_date"] = pd.to_datetime(
    retail_data["transaction_date"],
    errors="coerce"
)

print(
    "Invalid Dates:",
    retail_data["transaction_date"].isnull().sum()
)
print(
    "Minimum Date:",
    retail_data["transaction_date"].min()
)

print(
    "Maximum Date:",
    retail_data["transaction_date"].max()
)

#Personally Identifiable Information
def mask_email(email):
    email = str(email)

    if "@" not in email:
        return email

    name, domain = email.split("@")

    return name[0] + "***@" + domain
retail_data["email"] = retail_data["email"].apply(
    mask_email
)

#Phone masking
def mask_phone(phone):
    phone = str(phone)

    return "******" + phone[-4:]
retail_data["phone"] = retail_data["phone"].apply(
    mask_phone
)
print(
    retail_data[
        ["email", "phone"]
    ].head()
)

#Revenue
retail_data["revenue"] = (
    retail_data["price"]
    * retail_data["quantity"]
    * (1 - retail_data["discount"] / 100)
)
print(
    "Total Revenue:",
    retail_data["revenue"].sum()
)
#Create Business KPIs
revenue_by_category = (
    retail_data.groupby("category")["revenue"]
    .sum()
    .reset_index()
    .sort_values("revenue", ascending=False)
)

print(revenue_by_category)
revenue_by_city = (
    retail_data.groupby("city")["revenue"]
    .sum()
    .reset_index()
    .sort_values("revenue", ascending=False)
)

print(revenue_by_city)
best_selling_products = (
    retail_data.groupby("product_name")["quantity"]
    .sum()
    .reset_index()
    .sort_values("quantity", ascending=False)
)

print(best_selling_products)
retail_data["year_month"] = retail_data["transaction_date"].dt.to_period("M")

monthly_revenue = (
    retail_data.groupby("year_month")["revenue"]
    .sum()
    .reset_index()
)

print(monthly_revenue.head())


print("Final Record Count:", len(retail_data))

print(
    "Unique Customers:",
    retail_data["customer_id"].nunique()
)

#convert to csv file
output_folder = r"C:\Users\Neenu\Desktop\Retail_Data_Engineering_Project\Output"

retail_data.to_csv(
    os.path.join(output_folder, "cleaned_retail_data.csv"),
    index=False
)

revenue_by_category.to_csv(
    os.path.join(output_folder, "revenue_by_category.csv"),
    index=False
)

revenue_by_city.to_csv(
    os.path.join(output_folder, "revenue_by_city.csv"),
    index=False
)

best_selling_products.to_csv(
    os.path.join(output_folder, "best_selling_products.csv"),
    index=False
)

monthly_revenue.to_csv(
    os.path.join(output_folder, "monthly_revenue.csv"),
    index=False
)

print(retail_data.shape)
print(retail_data.head())
print(retail_data.isnull().sum())