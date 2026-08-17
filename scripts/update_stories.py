import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_meta(soup, prop=None, name=None):
    if prop:
        tag = soup.find("meta", attrs={"property": prop})
    else:
        tag = soup.find("meta", attrs={"name": name})
    return tag.get("content", "").strip() if tag else ""

stories = []

with open("articles.txt", "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

for url in urls:
    print(f"Reading {url}")

    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title = get_meta(soup, prop="og:title")
    image = get_meta(soup, prop="og:image")
    description = get_meta(soup, prop="og:description")
    published = get_meta(soup, prop="article:published_time")

    if not title and soup.title:
        title = soup.title.get_text(strip=True)

    if image:
        image = urljoin(url, image)

    stories.append({
        "url": url,
        "title": title,
        "image": image,
        "description": description,
        "published": published
    })

with open("stories.json", "w", encoding="utf-8") as f:
    json.dump(stories, f, ensure_ascii=False, indent=2)

print("stories.json created successfully")
