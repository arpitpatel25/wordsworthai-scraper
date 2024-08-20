from scrape_and_tag_main.models.brand_page_url import BrandPageURL
from scrape_and_tag_main.models.page_types_enum import PageType


def filter_brand_page_urls(brand_page_urls):
    """Filter BrandPageURL objects by page type."""
    product_objects = [obj for obj in brand_page_urls if obj.page_type == PageType.PRODUCTS.value]
    collection_objects = [obj for obj in brand_page_urls if obj.page_type == PageType.COLLECTIONS.value]
    return product_objects, collection_objects