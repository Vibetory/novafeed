from bs4 import BeautifulSoup

def extract_image(entry):
    """
    Try to extract an image from RSS entry (media:content, thumbnail, img in summary...)
    """

    # 1. media:content
    media_content = getattr(entry, "media_content", None)
    if media_content:
        if isinstance(media_content, list) and media_content:
            url = media_content[0].get("url")
            if url:
                return url

    # 2. media:thumbnail
    media_thumb = getattr(entry, "media_thumbnail", None)
    if media_thumb:
        if isinstance(media_thumb, list) and media_thumb:
            url = media_thumb[0].get("url")
            if url:
                return url

    # 3. direct "image" field
    image_attr = getattr(entry, "image", None)
    if isinstance(image_attr, dict):
        for key in ("url", "href", "link"):
            if image_attr.get(key):
                return image_attr[key]

    # 4. Parse <img> inside summary/content
    html = getattr(entry, "summary", "") or ""
    if hasattr(entry, "content"):
        html = entry.content[0].get("value", "") or html

    soup = BeautifulSoup(html, "html.parser")
    img = soup.find("img")
    if img and img.get("src"):
        return img["src"]

    return None
