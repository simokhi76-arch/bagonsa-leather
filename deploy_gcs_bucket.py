"""
Google Cloud Storage (GCS) Deployment Automation for BAGONSA.
Uploads all static assets from dist_pages/ to a Google Cloud Storage bucket
(storage.googleapis.com/{BUCKET_NAME}/) with correct Content-Type headers,
public read access, and cache-control optimization.
"""

import argparse
import mimetypes
import os
import sys
from pathlib import Path

# Ensure parent directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config

try:
    from google.cloud import storage
    from google.cloud.exceptions import GoogleCloudError
    GCS_LIBS_AVAILABLE = True
except ImportError:
    GCS_LIBS_AVAILABLE = False


CONTENT_TYPE_OVERRIDES = {
    ".html": "text/html; charset=utf-8",
    ".xml": "application/xml; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".json": "application/json; charset=utf-8",
}


def get_content_type(file_path: Path) -> str:
    """Returns accurate MIME content type for static files."""
    ext = file_path.suffix.lower()
    if ext in CONTENT_TYPE_OVERRIDES:
        return CONTENT_TYPE_OVERRIDES[ext]
    mime, _ = mimetypes.guess_type(str(file_path))
    return mime or "application/octet-stream"


def deploy_to_gcs(
    bucket_name: str,
    source_dir: Path,
    dry_run: bool = False,
    make_public: bool = True
):
    """Uploads directory contents to the specified Google Cloud Storage bucket."""
    print("=" * 65)
    print("BAGONSA GOOGLE CLOUD STORAGE DEPLOYMENT")
    print("=" * 65)
    print(f"Source Directory: {source_dir}")
    print(f"Target GCS Bucket: gs://{bucket_name}/")
    print(f"Public Base URL: https://storage.googleapis.com/{bucket_name}/")

    if not source_dir.exists():
        print(f"ERROR: Source directory {source_dir} does not exist. Run build_html_pages.py first.")
        sys.exit(1)

    files_to_upload = [p for p in source_dir.rglob("*") if p.is_file()]
    print(f"Discovered {len(files_to_upload)} files to deploy.")

    if dry_run:
        print("\n[DRY RUN MODE ENABLED] No files will be uploaded.")
        for i, f in enumerate(files_to_upload, start=1):
            rel = f.relative_to(source_dir).as_posix()
            ctype = get_content_type(f)
            print(f"  [{i}/{len(files_to_upload)}] Would upload: {rel} ({ctype}) -> gs://{bucket_name}/{rel}")
        print("\nDry run completed successfully.")
        return

    if not GCS_LIBS_AVAILABLE:
        print("\nERROR: google-cloud-storage is not installed.")
        print("Please install via: pip install google-cloud-storage")
        sys.exit(1)

    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)

        if not bucket.exists():
            print(f"Bucket '{bucket_name}' not found. Attempting to create bucket...")
            bucket = client.create_bucket(bucket_name)
            print(f"Created bucket '{bucket_name}'.")

        success_count = 0
        for i, f in enumerate(files_to_upload, start=1):
            rel_path = f.relative_to(source_dir).as_posix()
            blob = bucket.blob(rel_path)
            content_type = get_content_type(f)

            blob.content_type = content_type
            blob.cache_control = "public, max-age=3600"
            blob.upload_from_filename(str(f))

            if make_public:
                try:
                    blob.make_public()
                except Exception as acl_err:
                    # Uniform bucket-level access might disable individual ACLs
                    pass

            print(f"  [{i}/{len(files_to_upload)}] Uploaded: {rel_path} -> {blob.public_url}")
            success_count += 1

        print("\n" + "=" * 65)
        print(f"DEPLOY COMPLETE: Uploaded {success_count} files to gs://{bucket_name}/")
        print("=" * 65)

    except GoogleCloudError as gce:
        print(f"\nGoogle Cloud Error: {gce}")
        sys.exit(1)
    except Exception as ex:
        print(f"\nUnexpected Deployment Error: {ex}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Upload dist_pages/ to Google Cloud Storage bucket.")
    parser.add_argument(
        "--bucket",
        default=config.GCS_BUCKET_NAME,
        help="Google Cloud Storage bucket name"
    )
    parser.add_argument(
        "--dir",
        default=str(config.DIST_PAGES_DIR),
        help="Local source directory to upload"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate upload without transferring files"
    )
    parser.add_argument(
        "--no-public",
        action="store_true",
        help="Do not set public-read ACL on blobs"
    )

    args = parser.parse_args()
    deploy_to_gcs(
        bucket_name=args.bucket,
        source_dir=Path(args.dir),
        dry_run=args.dry_run,
        make_public=not args.no_public
    )


if __name__ == "__main__":
    main()
