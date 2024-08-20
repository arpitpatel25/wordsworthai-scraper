# import requests
# from bs4 import BeautifulSoup
# from PIL import Image
# from io import BytesIO
from scrape_and_tag_main.models.media_url import MediaUrl
from scrape_and_tag_main.models.page_types_enum import PageType, MediaType
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import subprocess
import os

def parse_srcset(srcset):
    srcset_list = []
    for item in srcset.split(","):
        parts = item.strip().split(" ")
        if len(parts) == 2:
            url, size = parts
        elif len(parts) == 1:
            url, size = parts[0], "default"

        if url.startswith("//"):
            url = "https:" + url

        srcset_list.append([size, url])
    return srcset_list


def get_video_dimensions(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open("temp_video.mp4", "wb") as f:
            f.write(response.content)
        file_size = os.path.getsize("temp_video.mp4")

        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "csv=s=x:p=0",
                "temp_video.mp4",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        width, height = map(int, result.stdout.decode("utf-8").strip().split("x"))
        return width, height, file_size
    except Exception as e:
        print(f"Error processing video for dimensions {url}: {e}")
        return None, None, None


def make_hashable(item):
    """Convert unhashable types within an object to hashable equivalents."""
    if isinstance(item, dict):
        return frozenset((key, make_hashable(value)) for key, value in item.items())
    elif isinstance(item, list):
        return tuple(make_hashable(x) for x in item)
    elif isinstance(item, MediaUrl):
        # Convert MediaUrl object to a hashable representation using its attributes
        return frozenset(item.to_mongo().to_dict().items())
    return item

def remove_duplicates(data_list):
    """Remove duplicates from a list of MediaUrl objects."""
    seen = set()
    unique_list = []
    for item in data_list:
        # Convert MediaUrl object to a hashable representation
        item_tuple = make_hashable(item)
        if item_tuple not in seen:
            seen.add(item_tuple)
            unique_list.append(item)
    return unique_list


def extract_background_images(soup):
    """Extract background images from elements with inline styles."""
    background_images = []
    for element in soup.find_all(style=True):
        style = element.get("style", "")
        if "background-image" in style or "background" in style:
            url_start = style.find("url(")
            url_end = style.find(")", url_start)
            if url_start != -1 and url_end != -1:
                img_url = style[url_start + 4 : url_end].strip("'\"")
                if img_url.startswith("//"):
                    img_url = "https:" + img_url

                try:
                    response = requests.get(img_url)
                    response.raise_for_status()
                    img_obj = Image.open(BytesIO(response.content))

                    background_images.append(
                        {
                            "url": img_url,
                            "aspect_ratio": img_obj.width / img_obj.height,
                            "file_size": len(response.content),
                            "type": "https",
                            "height": img_obj.height,
                            "width": img_obj.width,
                        }
                    )
                except Exception as e:
                    print(f"Error processing background image {img_url}: {e}")
    return background_images

def scrape_images_and_videos(brand_page):
    print("page_tyep-----> ",brand_page.page_type)
    url = brand_page.page_url
    page_type = brand_page.page_type
    print("page_tyep-----> 1",brand_page.page_type)

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"Error fetching page content: {e}")
        return []
    print("page_tyep-----> 2",brand_page.page_type)

    media_urls = []
    body = soup.body

    # Scrape images
    for img in body.find_all("img"):
        try:
            img_url = img.get("src")
            srcset = img.get("srcset", "")
            print("page_tyep-----> 3", brand_page.page_type)

            if img_url and not img_url.lower().endswith(".svg"):
                if img_url.startswith("//"):
                    img_url = "https:" + img_url
                print("page_tyep-----> 4", brand_page.page_type)

                response = requests.get(img_url)
                response.raise_for_status()
                img_obj = Image.open(BytesIO(response.content))

                media_url_obj = MediaUrl(
                    brand_base_url=brand_page.brand_base_url,
                    source_url=url,
                    source_page_type=page_type,
                    media_type=MediaType.IMAGE.value,
                    media_url=img_url,
                    aspect_ratio=img_obj.width / img_obj.height,
                    src_set=parse_srcset(srcset),
                    file_size=len(response.content),
                    type="https",
                    height=img_obj.height,
                    width=img_obj.width,
                )

                # Attach product or collection tags based on page type
                if page_type == PageType.PRODUCTS.value:
                    media_url_obj.product_tag = brand_page.handle
                    media_url_obj.collection_tag = ""
                elif page_type == PageType.COLLECTIONS.value:
                    media_url_obj.collection_tag = brand_page.handle
                    media_url_obj.product_tag = ""

                media_urls.append(media_url_obj)
                print("page_tyep----->5 ", brand_page.page_type)

        except Exception as e:
            print(f"Error processing image {img_url}: {e}")
            continue
    print("page_tyep-----> 7",brand_page.page_type)

    # Scrape videos
    for video in body.find_all("video"):
        print("page_tyep-----> 8", brand_page.page_type)

        try:
            video_url = video.get("src")
            video_sources = video.find_all("source")
            src_set = []
            width, height, file_size = None, None, None

            for source in video_sources:
                try:
                    source_url = source.get("src")
                    source_format = source.get("type", "unknown")
                    if source_url:
                        if source_url.startswith("//"):
                            source_url = "https:" + source_url
                        src_set.append([source_format, source_url])
                        if not video_url:
                            video_url = source_url
                except Exception as e:
                    print(f"Error processing video source: {e}")
                    continue

            if video_url:
                width, height, file_size = get_video_dimensions(video_url)

            if video_url and width and height and file_size:
                print("page_tyep-----> 9", brand_page.page_type)

                media_url_obj = MediaUrl(
                    brand_base_url=brand_page.brand_base_url,
                    source_url=url,
                    source_page_type=page_type,
                    media_type=MediaType.VIDEO.value,
                    media_url=video_url,
                    aspect_ratio=width / height,
                    src_set=src_set,
                    file_size=file_size,
                    type="https",
                    height=height,
                    width=width,
                )
                print("scrapping VIDEO ------->: ",media_url_obj.media_url )


                # Attach product or collection tags based on page type
                if page_type == PageType.PRODUCTS.value:
                    media_url_obj.product_tag = brand_page.handle
                elif page_type == PageType.COLLECTIONS.value:
                    media_url_obj.collection_tag = brand_page.handle

                media_urls.append(media_url_obj)
            print("page_tyep-----> 10", brand_page.page_type)

        except Exception as e:
            print(f"Error processing video {video_url}: {e}")
            continue

    # media_urls = remove_duplicates(media_urls)
    print("page_tyep-- ExIT---> ",brand_page.page_type)

    return media_urls
