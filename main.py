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
    
    # Let's extract the product link
    product_link_tag = product.find('a')
    product_info['product_url'] = product_link_tag['href'] if product_link_tag else 'N/A'
    
    # Lets extract product image by checking the src attribute that starts with the desired URL
    product_image_tag = product.find('img', src=True)
    product_image_url = product_image_tag['src'] if product_image_tag and "https://scrapingcourse.com/ecommerce/wp-content" in product_image_tag['src'] else 'N/A'
    product_info['image_url'] = product_image_url
    
    # Lets extract product name
    product_name_tag = product.find('span', class_='product-name')
    product_info['name'] = product_name_tag.text.strip() if product_name_tag else 'N/A'
    
    # Lets extract product price
    product_price_tag = product.find('span', class_='product-price')
    product_info['price'] = product_price_tag.text.strip() if product_price_tag else 'N/A'
    
    return product_info

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

# Print all products
for p in all_products:
    print(p)

# Save the scraped data to a CSV file
df = pd.DataFrame(all_products)
df.to_csv('scraped_products.csv', index=False)
print('Product data saved to scraped_products.csv')
