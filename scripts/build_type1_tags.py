
import requests
from bs4 import BeautifulSoup
from scrape_and_tag_main.models.brand_page_url import BrandPageURL
from scrape_and_tag_main.models.page_types_enum import PageType


def scrape_main_content_and_tags(url, product_objects, collection_objects):
    # Step 1: Get the HTML content of the page
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Step 2: Extract the HTML content within the <main> tag
    main_content = soup.find("main")
    if not main_content:
        return [], [], []  # Return empty sets if <main> tag is not found

    # Save the extracted <main> content to a file (for debugging)
    with open("extracted_main_content_testing.html", "w", encoding="utf-8") as file:
        file.write(main_content.prettify())

    # Step 3: Extract all <a> tags and their hrefs within the <main> content
    a_tags = main_content.find_all("a", href=True)

    # Initialize sets to store matching tags (to avoid duplicates)
    product_tags = set()
    collection_tags = set()
    product_tags_for_title = set()

    # Step 4: Check hrefs against product and collection handles
    for a_tag in a_tags:
        href = a_tag.get("href")
        for product in product_objects:
            if product.handle in href:
                product_tags.add(product.handle)
        for collection in collection_objects:
            if collection.handle in href:
                collection_tags.add(collection.handle)

    # Step 5: Check if product titles are in the text content of the <main> content
    main_text = main_content.get_text()
    for product in product_objects:
        if product.title in main_text:
            product_tags_for_title.add(product.handle)

    # Return the filled sets as lists
    print("----------------t1>")
    print(list(product_tags), list(collection_tags), list(product_tags_for_title))
    return list(product_tags), list(collection_tags), list(product_tags_for_title)

def scrape_tags_for_page_1(url, product_objects, collection_objects):
    """Main function to scrape tags for a given page URL and list of BrandPageURL objects."""
    # Filter BrandPageURL objects by page type
    # product_objects, collection_objects = filter_brand_page_urls(brand_page_urls)

    # Scrape the page and generate tags
    product_tags, collection_tags, product_tags_for_title = scrape_main_content_and_tags(
        url, product_objects, collection_objects
    )

    return product_tags, collection_tags, product_tags_for_title


