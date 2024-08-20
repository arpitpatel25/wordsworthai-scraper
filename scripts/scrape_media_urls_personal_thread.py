from scrape_and_tag_main.models.brand_page_url import BrandPageURL
from scrape_and_tag_main.models.page_types_enum import PageType
from scrape_and_tag_main.utils.openai_object_tags_generator import process_image_with_openai
from scrape_and_tag_main.scripts.scrape_images_and_videos import scrape_images_and_videos
from scrape_and_tag_main.scripts.build_type1_tags import scrape_tags_for_page_1
from scrape_and_tag_main.scripts.build_type2_tags import scrape_tags_for_page_2
from scrape_and_tag_main.utils.filter_brand_page_urls import filter_brand_page_urls

import concurrent.futures
from tqdm import tqdm

def fetch_and_process(base_url):
    try:
        # Fetch all URLs from MongoDB
        brand_pages = BrandPageURL.objects(brand_base_url=base_url)
        product_objects, collection_objects = filter_brand_page_urls(brand_pages)

        if not brand_pages:
            print(f"No pages found for base URL: {base_url}")
            return

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            list(tqdm(executor.map(lambda page: process_page(page, product_objects, collection_objects), brand_pages),
                      total=len(brand_pages)))



    except Exception as e:
        print(f"Error fetching and processing data: {e}")


def process_page(page, product_objects, collection_objects):
    # todo: remove this ---->
    # page.page_url = "https://vitahustle.com/pages/9-reasons-why-kev"

    print(f"Processing page: {page.page_url}")
    p1_t1, p1_t2, p1_t3 = [], [], []
    p2_t1, p2_t2, p2_t3 = [], [], []

    if page.page_type == PageType.PAGES.value:
        p1_t1, p1_t2, p1_t3 = scrape_tags_for_page_1(page.page_url, product_objects, collection_objects)
        p2_t1, p2_t2, p2_t3 = scrape_tags_for_page_2(page.page_url, product_objects, collection_objects)

    # todo: remove this ---->
    # else:
    #     continue
    # Scrape images and videos from the page
    try:
        media_urls = scrape_images_and_videos(page)
    except Exception as e:
        print("Unknown failure while scraping")
        media_urls = []

    # Process each media URL
    for media in media_urls:
        if media.media_type == 'image':
            # Get tags using OpenAI for images
            # tags = process_image_with_openai(media.media_url)
            # media.has_human = tags[0] == 'True'
            # media.has_product = tags[1] == 'True'
            # media.has_multiple_products = tags[2] == 'True'
            media.has_human = False
            media.has_product = False
            media.has_multiple_products = False

        # if page.page_type == PageType.PAGES.value:
        media.product_tags_main_node_a_tags = p1_t1
        media.collection_tags_main_node_a_tags = p1_t2
        media.product_tags_main_node_text = p1_t3

        media.product_tags_xpath_a_tags = p2_t1
        media.collections_tags_xpath_a_tags = p2_t2
        media.product_tags_xpath_text = p2_t3

        # Save the media URL to MongoDB
        # todo: uncomment this ---->

        media.save()
        # todo: remove this ---->

        print(media)
        print(media.source_page_type)
        print(media.source_url)
        print(media.media_url)
        print(media.product_tags_main_node_a_tags)
        print(media.product_tags_main_node_text)
        print(media.collection_tags_main_node_a_tags)
        print(media.product_tags_xpath_a_tags)
        print(media.collections_tags_xpath_a_tags)
        print(media.product_tags_xpath_text)
        # break

    # todo: remove this ---->

    # if page.page_type == PageType.PAGES.value:
    # break

    print(f"Finished processing page: {page.page_url}")