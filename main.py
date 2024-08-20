
import sys
import argparse
from mongoengine import connect
from models.brand_page_url import BrandPageURL
from models.media_url import MediaUrl
from scripts.store_brand_page_urls import store_brand_page_urls
from scripts.scrape_media_urls import fetch_and_process
# from scripts.scrape_media_urls_personal_thread import fetch_and_process

# Connect to MongoDB
from config import Config

connect(**Config.MONGODB_SETTINGS)


def store_urls(base_url):
    """Store brand page URLs."""
    print(f"Storing brand page URLs for {base_url}...")
    store_brand_page_urls(base_url)
    print("Brand page URLs have been stored successfully.")


def scrape(base_url):
    """Scrape and tag media URLs."""
    print(f"Scraping and tagging pages for {base_url}...")
    fetch_and_process(base_url)
    print("Tagged pages have been stored successfully.")


def test_connection():
    """Test MongoDB connection."""
    try:
        count = BrandPageURL.objects.count()
        print(f"MongoDB connection successful! BrandPageURL count: {count}")
        count = MediaUrl.objects.count()
        print(f"MongoDB connection successful! MediaUrl---- count: {count}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="Shopify Scraper CLI")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Store URLs command
    store_parser = subparsers.add_parser("store-urls", help="Store brand page URLs")
    store_parser.add_argument('--base_url', required=True, help="Base URL for storing brand page URLs")

    # Scrape and tag command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape and tag media URLs")
    scrape_parser.add_argument('--base_url', required=True, help="Base URL for scraping and tagging pages")

    # Test connection command
    subparsers.add_parser("test-connection", help="Test MongoDB connection")

    args = parser.parse_args()

    if args.command == "store-urls":
        store_urls(args.base_url)
    elif args.command == "scrape":
        scrape(args.base_url)
    elif args.command == "test-connection":
        test_connection()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
