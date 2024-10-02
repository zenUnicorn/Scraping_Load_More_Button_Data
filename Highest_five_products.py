import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

# Define headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# Base URL with pagination
base_url = "https://www.scrapingcourse.com/ajax/products?offset={}"

# Function to extract product details
def extract_product_info(product):
    product_info = {}
    
    # Extract the product link
    product_link_tag = product.find('a')
    product_info['product_url'] = product_link_tag['href'] if product_link_tag else 'N/A'
    
    # Extract product image
    product_image_tag = product.find('img', src=True)
    product_image_url = product_image_tag['src'] if product_image_tag and "https://scrapingcourse.com/ecommerce/wp-content" in product_image_tag['src'] else 'N/A'
    product_info['image_url'] = product_image_url
    
    # Extract product name
    product_name_tag = product.find('span', class_='product-name')
    product_info['name'] = product_name_tag.text.strip() if product_name_tag else 'N/A'
    
    # Extract product price (convert to float for later sorting)
    product_price_tag = product.find('span', class_='product-price')
    price_text = product_price_tag.text.strip() if product_price_tag else 'N/A'
    product_info['price'] = float(price_text.replace('$', '').replace(',', '')) if price_text != 'N/A' else 0.0
    
    return product_info

# Function to extract product description and SKU from product page
def extract_product_details(product_url):
    product_details = {}
    
    # Fetch the product page
    response = requests.get(product_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to retrieve product page: {product_url}")
        product_details['description'] = 'N/A'
        product_details['sku'] = 'N/A'
        return product_details
    
    # Parse the product page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the parent div containing the description
    description_div = soup.find('div', class_='woocommerce-Tabs-panel woocommerce-Tabs-panel--description panel entry-content wc-tab')

    # If the div is found, extract all <p> tags inside it
    if description_div:
        description_paragraphs = description_div.find_all('p')
        # Join all <p> tag content together into one string
        product_details['description'] = ' '.join([p.text.strip() for p in description_paragraphs])
    else:
        product_details['description'] = 'N/A'
    
    # Extract SKU
    sku_tag = soup.find('span', class_='sku') or soup.find('div', class_='sku')
    product_details['sku'] = sku_tag.text.strip() if sku_tag else 'N/A'
    
    return product_details

# Start pagination from offset 10
offset = 10
all_products = []  # List to hold all scraped products

# Loop through pages
while True:
    # Fetch the page with the current offset
    response = requests.get(base_url.format(offset), headers=headers)
    
    # Check if the request was successful
    if response.status_code != 200:
        print("Failed to retrieve page, stopping the scraper.")
        break
    
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all product listings on the page
    product_listings = soup.find_all("div", class_="product-item flex flex-col items-center rounded-lg")
    
    # If there are no more products, exit the loop
    if not product_listings:
        print("No more products found, exiting the loop.")
        break
    
    # Loop through each product and extract details
    for product in product_listings:
        product_info = extract_product_info(product)
        all_products.append(product_info)
    
    # Print the number of products scraped so far
    print(f"Scraped {len(all_products)} products.")
    
    # Simulate the load more button by incrementing the offset
    offset += 20  # Assuming each page loads 20 products

    # Introduce a short delay to avoid overloading the server
    time.sleep(2)

# Convert the list of products into a DataFrame
df = pd.DataFrame(all_products)

# Sort products by price in descending order to get the 5 highest-priced products
top_5_products = df.sort_values(by='price', ascending=False).head(5)

# Initialize lists to store descriptions and SKUs for the top 5 products
descriptions = []
skus = []

# Extract descriptions and SKUs for the top 5 products
for index, row in top_5_products.iterrows():
    product_details = extract_product_details(row['product_url'])
    descriptions.append(product_details['description'])
    skus.append(product_details['sku'])

# Add the extracted descriptions and SKUs to the top 5 products DataFrame
top_5_products['description'] = descriptions
top_5_products['sku'] = skus

# Save the top 5 products data to a CSV file
top_5_products.to_csv('top_5_highest_priced_products.csv', index=False)

print('Top 5 highest-priced products data saved to top_5_highest_priced_products.csv')
