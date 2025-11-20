import csv
from modules.feeds import FEEDS_CSV_PATH


FEED_FIELDS = [
    "name",
    "url",
    "domains",
    "themes",
    "source_ranking",
    "ranking_author"
]


def load_sources():
    """Charge les sources depuis feeds.csv."""
    sources = []
    with open(FEEDS_CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sources.append(row)
    return sources


def save_sources(sources):
    """Réécrit feeds.csv proprement."""
    with open(FEEDS_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FEED_FIELDS)
        writer.writeheader()
        for s in sources:
            writer.writerow(s)


def add_source(data):
    """Ajoute une nouvelle source RSS."""
    sources = load_sources()
    sources.append(data)
    save_sources(sources)


def update_source(index, data):
    """Modifie une source (par index)."""
    sources = load_sources()
    sources[index] = data
    save_sources(sources)


def delete_source(index):
    """Supprime une source RSS."""
    sources = load_sources()
    sources.pop(index)
    save_sources(sources)
