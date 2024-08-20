import requests
from bs4 import BeautifulSoup
from scrape_and_tag_main.models.brand_page_url import BrandPageURL
from scrape_and_tag_main.models.page_types_enum import PageType


def scrape_filtered_content_and_tags(url, product_objects, collection_objects):
    # Step 1: Get the HTML content of the page using requests
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Step 2: Extract the <body> content
    body_content = soup.find("body")
    if not body_content:
        return [], [], []  # Return empty lists if <body> tag is not found

    # Step 3: Remove unwanted elements within the <body> (header, footer, nav, aside, head, script, side-drawer, style)
    for tag in body_content.find_all(
        ["header", "footer", "nav", "aside", "script", "side-drawer", "style"]
    ):
        tag.decompose()

    # Remove elements where the tag name contains "nav" or "side"
    for tag in body_content.find_all():
        if tag.name and ("nav" in tag.name or "side" in tag.name):
            tag.decompose()

    # Step 4: Remove elements with unwanted classes or IDs that contain "side-drawer", "header", or "footer"
    for tag in body_content.find_all(attrs={"class": lambda c: c and "side-drawer" in c}):
        tag.decompose()
    for tag in body_content.find_all(attrs={"id": lambda i: i and "side-drawer" in i}):
        tag.decompose()
    for tag in body_content.find_all(attrs={"id": lambda i: i and "header" in i}):
        tag.decompose()
    for tag in body_content.find_all(attrs={"id": lambda i: i and "footer" in i}):
        tag.decompose()

    # Extract the filtered HTML content into a variable
    filtered_html = body_content.prettify()

    # Save the filtered HTML content to a file (for debugging)
    with open("extracted_filtered_content_body.html", "w", encoding="utf-8") as file:
        file.write(filtered_html)

    # Step 5: Extract all <a> tags and their hrefs within the filtered content
    a_tags = body_content.find_all("a", href=True)

    # Initialize sets to store matching tags (to avoid duplicates)
    product_tags = set()
    collection_tags = set()
    product_tags_for_title = set()

    # Step 6: Check hrefs against product and collection handles
    for a_tag in a_tags:
        href = a_tag.get("href")
        for product in product_objects:
            if product.handle in href:
                product_tags.add(product.handle)
        for collection in collection_objects:
            if collection.handle in href:
                collection_tags.add(collection.handle)

    # Step 7: Check if product titles are in the text content of the filtered content
    filtered_text = body_content.get_text()
    for product in product_objects:
        if product.title in filtered_text:
            product_tags_for_title.add(product.handle)

    # Convert sets to lists before returning, if needed
    print("----------------t2>")
    print(list(product_tags), list(collection_tags), list(product_tags_for_title))
    return list(product_tags), list(collection_tags), list(product_tags_for_title)

def scrape_tags_for_page_2(url, product_objects, collection_objects):
    """Main function to scrape tags for a given page URL and list of BrandPageURL objects."""
    # Filter BrandPageURL objects by page type

    # Scrape the page and generate tags
    product_tags, collection_tags, product_tags_for_title = scrape_filtered_content_and_tags(
        url,  product_objects, collection_objects
    )

    return product_tags, collection_tags, product_tags_for_title

