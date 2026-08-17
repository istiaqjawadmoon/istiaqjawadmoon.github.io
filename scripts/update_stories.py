import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

AUTHOR_URL = "https://gnv.news/archives/author/mohammad-istiaq-jawad"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_meta(soup, prop=None, name=None):
    if prop:
        tag = soup.find("meta", attrs={"property": prop})
    else:
        tag = soup.find("meta", attrs={"name": name})
    return tag.get("content", "").strip() if tag else ""

def find_article_urls():
    urls = []
    page = 1

    while True:
        page_url = AUTHOR_URL if page == 1 else f"{AUTHOR_URL}/page/{page}/"
        print(f"Checking author page: {page_url}")

        response = requests.get(page_url, headers=HEADERS, timeout=20)

        if response.status_code == 404:
            break

        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        page_urls = []

        for heading in soup.find_all(["h2", "h3"]):
            link = heading.find("a", href=True)
            if not link:
                continue

            url = urljoin(page_url, link["href"])

            if "/archives/" in url and "/author/" not in url and "/category/" not in url:
                page_urls.append(url)

        page_urls = list(dict.fromkeys(page_urls))
        new_urls = [url for url in page_urls if url not in urls]

        if not new_urls:
            break

        urls.extend(new_urls)
        page += 1

    return urls

article_urls = find_article_urls()

print(f"Found {len(article_urls)} articles")

stories = []

for url in article_urls:
    print(f"Reading article: {url}")

    try:
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

    except Exception as e:
        print(f"Could not process {url}: {e}")

stories.sort(
    key=lambda story: story.get("published") or "",
    reverse=True
)

with open("stories.json", "w", encoding="utf-8") as f:
    json.dump(stories, f, ensure_ascii=False, indent=2)

print(f"stories.json created with {len(stories)} articles")
