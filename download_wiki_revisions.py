import argparse
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

DATA_DIR = Path("data")


def download_page_w_revisions(page_title: str, limit: int = 100):
    base_url = "https://en.wikipedia.org/w/index.php"
    params = {
        "title": "Special:Export",
        "pages": page_title,
        "limit": min(limit, 1000),  # Wikipedia API limits to 1000 revisions
        "update": False,
        "dir": "desc",
        "action": "submit",
    }
    response = requests.post(base_url, data=params)
    response.raise_for_status()
    return response.text


def parse_mediawiki_revisions(xml_content):
    soup = BeautifulSoup(xml_content, "lxml-xml")
    for revision in soup.find_all("revision"):
        yield str(revision)


def extract_id(revision: str) -> str:
    return str(_extract_attribute(revision, attribute="id"))


def find_timestamp(revision: str) -> datetime:
    return parse_timestring(_extract_attribute(revision, attribute="timestamp"))


def _extract_attribute(text: str, attribute: str = "timestamp") -> str:
    soup = BeautifulSoup(text, "lxml-xml")
    result = soup.find(attribute)
    if result is None:
        raise ValueError(f"Could not find attribute {attribute} in text")
    return result.text


def parse_timestring(timestring: str) -> datetime:
    return datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%SZ")


def extract_yearmonth(timestamp: datetime) -> str:
    return timestamp.strftime("%Y-%m")


def find_yearmonth(revision: str) -> str:
    return extract_yearmonth(find_timestamp(revision))

def count_files(data_dir: Path, page: str, folders: False):
    page_path = data_dir / page
    if not page_path.exists(): return 0
    if folders:
        return sum(1 for x in page_path.glob("*") if x.is_file())
    else:
        return sum(1 for _ in page_path.glob('*'))

def main(page: str, limit: int, update:bool, data_dir: Path):
    """
    Downloads the main page (with revisions) for the given page title.
    Organizes the revisions into a folder structure like
    <page_name>/<year>/<month>/<revision_id>.xml
    """
    if update:
        print(f"Downloading {limit} revisions of {page} to {data_dir}, skip update set to {update}")
        raw_revisions = download_page_w_revisions(page, limit=limit)
        validate_page(page, page_xml=raw_revisions)
        print("Downloaded revisions. Parsing and saving...")
        for wiki_revision in tqdm(parse_mediawiki_revisions(raw_revisions), total=limit):
            revision_path = construct_path(
                wiki_revision=wiki_revision, page_name=page, save_dir=data_dir
            )
            if not revision_path.exists():
                revision_path.parent.mkdir(parents=True, exist_ok=True)
            revision_path.write_text(wiki_revision)
        
        print("Done!") # You should call count_revisions() here and print the number of revisions
                    # You should also pass an 'update' argument so that you can decide whether
                    # to update and refresh or whether to simply count the revisions.
    else:
        n_revision = count_files(data_dir=data_dir,page=page,folders=False)
        print(f"Update skipped, {n_revision} of revisions found. To update the revisions, parse in a True update flag.")
           


def construct_path(page_name: str, save_dir: Path, wiki_revision: str) -> Path:
    revision_id = extract_id(wiki_revision)
    timestamp = find_timestamp(wiki_revision)
    year = str(timestamp.year)
    month = str(timestamp.month).zfill(2)
    revision_path = save_dir / page_name / year / month / f"{revision_id}.xml"
    return revision_path


def validate_page(page_name: str, page_xml: str) -> None:
    try:
        _ = _extract_attribute(page_xml, attribute="page")
    except ValueError:
        raise ValueError(f"Page {page_name} does not exist")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download Wikipedia page revisions",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("page", type=str, help="Title of the Wikipedia page")
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of revisions to download",
    )
    parser.add_argument(
        "--update",
        type=bool,
        default=False,
        help="Flag for skips in updates"
    )
    args = parser.parse_args()
    main(page=args.page, limit=args.limit, update=args.update, data_dir=DATA_DIR)
