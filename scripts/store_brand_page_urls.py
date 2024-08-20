
from scrape_and_tag_main.models.brand_page_url import BrandPageURL
from scrape_and_tag_main.utils.download_json import download_json
from scrape_and_tag_main.models.page_types_enum import PageType
# from ..models.brand_page_url import BrandPageURL
# from ..utils.download_json import download_json
# from ..models.page_types_enum import PageType

def store_brand_page_urls(base_url):
    try:
        # Download JSON data
        collections_json = download_json(base_url, 'collections')
        print(f"Downloaded {len(collections_json.get('collections', []))} collections.")

        products_json = download_json(base_url, 'products')
        print(f"Downloaded {len(products_json.get('products', []))} products.")

        pages_json = download_json(base_url, 'pages')
        print(f"Downloaded {len(pages_json.get('pages', []))} pages.")

        # Add a new page object to the pages_json
        # pages_json['pages'].append({
        #     "brand_base_url": base_url,
        #     "page_type": "pages",
        #     "title": "Home",
        #     "handle": "home",
        #     "page_url": base_url
        # })

        # Upload data to MongoDB
        upload_to_mongodb(base_url, collections_json, PageType.COLLECTIONS.value)
        upload_to_mongodb(base_url, products_json, PageType.PRODUCTS.value)
        upload_to_mongodb(base_url, pages_json, PageType.PAGES.value)

        print("Data successfully uploaded to MongoDB.")

    except Exception as e:
        print(f"An error occurred: {e}")


def upload_to_mongodb(base_url, data, page_type):
    try:
        items = data.get(page_type, [])  # Use the page_type to get the list from JSON
        if not items:
            print(f"No items found for {page_type}.")
            return

        print(f"Uploading {len(items)} items of type {page_type} to MongoDB.")

        for item in items:
            try:
                url = f"{base_url}{page_type}/{item.get('handle', '')}"
                BrandPageURL(
                    brand_base_url=base_url,
                    page_type=page_type,
                    title=item.get('title', ''),
                    handle=item.get('handle', ''),
                    page_url=url
                ).save()
                print(f"Successfully uploaded {page_type} with handle {item.get('handle', '')}.")
            except Exception as e:
                print(f"Error uploading {page_type} with handle {item.get('handle', '')}: {e}")

    except Exception as e:
        print(f"Error in upload_to_mongodb: {e}")
