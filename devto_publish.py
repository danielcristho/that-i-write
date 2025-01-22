import requests, os
from dotenv import load_dotenv

load_dotenv()

def publish_to_devto(file_path, title, tags=None, published=True):
    api_key = os.getenv("DEV_TO_API_KEY")
    if not api_key:
        print("API Key not found! Check your .env file.")
        return

    # Read content from markdown file
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            body_markdown = file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    payload = {
        "article": {
            "title": title,
            "body_markdown": body_markdown,
            "tags": tags or [],
            "published": published
        }
    }

    response = requests.post("https://dev.to/api/articles", json=payload, headers=headers)
    if response.status_code == 201:
        print("Article published successfully!")
        print(response.json())
    else:
        print(f"Failed to publish article. Status code: {response.status_code}")
        print(response.json())

if __name__ == "__main__":
    # Path to the markdown file
    file_path = "read-from-book/kubernetes-untuk-pemula/kubernetes103-object.md"

    # Define article title and tags
    title = "Kubernetes 103: Object"
    tags = ["Kubernetes", "Beginners", "DevOps"]

    # Publish article
    publish_to_devto(file_path, title, tags)