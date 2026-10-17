"""
Google Indexing API Batch Automation for BAGONSA.
Reads sitemap.xml and submits URLs to the Google Indexing API
(indexing.googleapis.com/v3/urlNotifications:publish) using a Google Cloud
Service Account with automated rate limiting and dry-run testing support.
"""

import argparse
import os
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List

# Ensure parent directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_LIBS_AVAILABLE = True
except ImportError:
    GOOGLE_LIBS_AVAILABLE = False


INDEXING_SCOPES = ["https://www.googleapis.com/auth/indexing"]
INDEXING_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"


def parse_sitemap_urls(sitemap_path: Path) -> List[str]:
    """Parses all URL locations (<loc>) from a standard XML sitemap."""
    if not sitemap_path.exists():
        raise FileNotFoundError(f"Sitemap file not found at: {sitemap_path}")

    tree = ET.parse(sitemap_path)
    root = tree.getroot()
    
    # Handle XML namespace
    namespaces = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = []
    
    # Try with namespace first, fallback to without
    loc_nodes = root.findall(".//ns:loc", namespaces)
    if not loc_nodes:
        loc_nodes = root.findall(".//loc")

    for loc in loc_nodes:
        if loc.text:
            urls.append(loc.text.strip())

    return urls


def publish_url_notification(
    indexing_service,
    url: str,
    notification_type: str = "URL_UPDATED"
) -> dict:
    """Submits a single URL publish notification to Google Indexing API."""
    body = {
        "url": url,
        "type": notification_type
    }
    response = indexing_service.urlNotifications().publish(body=body).execute()
    return response


def run_indexer(
    key_file: str,
    sitemap_path: str,
    limit: int = 0,
    delay: float = 1.0,
    dry_run: bool = False
):
    """Executes the batch indexing workflow."""
    print("=" * 65)
    print("BAGONSA GOOGLE INDEXING API AUTOMATION")
    print("=" * 65)

    sitemap_file = Path(sitemap_path)
    urls = parse_sitemap_urls(sitemap_file)
    print(f"Extracted {len(urls)} URLs from {sitemap_file.name}")

    if limit > 0:
        urls = urls[:limit]
        print(f"Applying limit: submitting first {limit} URLs")

    if dry_run:
        print("\n[DRY RUN MODE ENABLED] No live requests will be sent to Google API.")
        for i, url in enumerate(urls, start=1):
            print(f"  [{i}/{len(urls)}] Would submit: {url}")
        print("\nDry run completed successfully.")
        return

    if not GOOGLE_LIBS_AVAILABLE:
        print("\nERROR: Required Google libraries are not installed.")
        print("Please install via: pip install google-api-python-client google-auth google-auth-httplib2")
        sys.exit(1)

    key_path = Path(key_file)
    if not key_path.exists():
        print(f"\nERROR: Service Account Key not found at: {key_path}")
        print("Place your service_account.json in the project root or set GOOGLE_APPLICATION_CREDENTIALS.")
        print("Tip: Test the pipeline using --dry-run")
        sys.exit(1)

    print(f"Authenticating with Service Account Key: {key_path.name}...")
    credentials = service_account.Credentials.from_service_account_file(
        str(key_path),
        scopes=INDEXING_SCOPES
    )
    indexing_service = build("indexing", "v3", credentials=credentials)
    print("Authentication successful. Initializing batch submissions...\n")

    success_count = 0
    error_count = 0

    for i, url in enumerate(urls, start=1):
        try:
            resp = publish_url_notification(indexing_service, url)
            notify_time = resp.get("urlNotificationMetadata", {}).get("latestUpdate", {}).get("notifyTime", "N/A")
            print(f"  [{i}/{len(urls)}] SUCCESS -> {url} (Google Timestamp: {notify_time})")
            success_count += 1
        except HttpError as err:
            print(f"  [{i}/{len(urls)}] HTTP ERROR for {url}: {err}")
            error_count += 1
        except Exception as ex:
            print(f"  [{i}/{len(urls)}] UNEXPECTED ERROR for {url}: {ex}")
            error_count += 1

        if i < len(urls) and delay > 0:
            time.sleep(delay)

    print("\n" + "=" * 65)
    print(f"BATCH COMPLETE: {success_count} Succeeded, {error_count} Failed out of {len(urls)} total URLs.")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="Submit sitemap URLs to Google Indexing API.")
    parser.add_argument(
        "--key-file",
        default=config.SERVICE_ACCOUNT_KEY_PATH,
        help="Path to Google Cloud service_account.json key"
    )
    parser.add_argument(
        "--sitemap-path",
        default=str(config.DIST_PAGES_DIR / "sitemap.xml"),
        help="Path to dist_pages/sitemap.xml"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit number of URLs to submit (0 = all URLs)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=config.INDEXING_RATE_LIMIT_DELAY,
        help="Delay in seconds between API requests (prevents quota spikes)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the submission process without sending API requests"
    )

    args = parser.parse_args()
    run_indexer(
        key_file=args.key_file,
        sitemap_path=args.sitemap_path,
        limit=args.limit,
        delay=args.delay,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
