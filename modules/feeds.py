import csv

FEEDS_CSV_PATH = "data/feeds.csv"


def load_feeds():
    feeds = []
    with open(FEEDS_CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            feeds.append({
                "name": row["name"],
                "url": row["url"],
                "domains": [d.strip() for d in row["domains"].split(",")],
                "themes": [t.strip() for t in row["themes"].split(",")],
                "source_ranking": int(row["source_ranking"]),
                "ranking_author": row["ranking_author"]
            })
    return feeds


def get_available_domains():
    domains = set()
    for feed in load_feeds():
        for d in feed["domains"]:
            domains.add(d)
    return sorted(domains)


def get_available_themes():
    themes = set()
    for feed in load_feeds():
        for t in feed["themes"]:
            themes.add(t)
    return sorted(themes)
