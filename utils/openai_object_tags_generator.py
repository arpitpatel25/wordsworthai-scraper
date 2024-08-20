import requests
import base64
import os
import re
from dotenv import load_dotenv
from prompt_image_detection import prompt

load_dotenv()

def process_image_with_openai(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()

        image_base64 = base64.b64encode(response.content).decode("utf-8")
        mime_type = "image/jpeg"
        image_data_url = f"data:{mime_type};base64,{image_base64}"

        image_data = {"type": "image_url", "image_url": {"url": image_data_url}}
        payload = {
            "model": "gpt-4o",  # Use the correct model name
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}, image_data],
                }
            ],
            "max_tokens": 300,
        }

        headers = {
            "Authorization": "Bearer {}".format(os.getenv("OPENAI_API_KEY")),
            "Content-Type": "application/json",
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions", json=payload, headers=headers
        )

        if response.status_code == 200:
            response_data = response.json()
            result = response_data["choices"][0]["message"]["content"]
            print("result original: ", result)

            # Use case-insensitive regex to find all variations of "true" and "false"
            bool_values = re.findall(r'\btrue\b|\bfalse\b', result, re.IGNORECASE)

            # Convert to title case
            bool_values = [value.capitalize() for value in bool_values]

            # Ensure list has exactly 3 elements
            if len(bool_values) < 3:
                bool_values.extend(["False"] * (3 - len(bool_values)))

            return bool_values[:3]

        else:
            raise Exception(
                "API call failed with status {}: {}".format(
                    response.status_code, response.text
                )
            )

    except requests.exceptions.RequestException as e:
        print(f"Error downloading the image: {e}")
        return ["False", "False", "False"]
    except Exception as e:
        print(f"Error processing the API request: {e}")
        return ["False", "False", "False"]

# Example usage
# image_url = "https://global.solawave.co/cdn/shop/files/20210608_SHOT08_1859_1-min.jpg?v=1660398952"
# image_url = "https://global.solawave.co/cdn/shop/files/ByeAcne_Vertical_Charcoal.webp?v=1720825493"


# image_url = "https://global.solawave.co/cdn/shop/files/Group_1_1.png?v=1662381541"

# image_url = "https://global.solawave.co/cdn/shop/files/charcoal_50x50.png"
# image_url = "https://global.solawave.co/cdn/shop/files/Group_48096259-min.jpg?v=1660398953"
# result = process_image_with_openai(image_url, prompt)
# print(result)
