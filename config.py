"""
Central configuration for BAGONSA Programmatic & Parasite SEO Automation Engine.
Stores domain paths, product silos, GitHub/Colab endpoints, GCS bucket details,
and indexing parameters.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DIST_PAGES_DIR = BASE_DIR / "dist_pages"
DIST_COLAB_DIR = BASE_DIR / "dist_colab"
SRC_DIR = BASE_DIR / "src"
KEYWORDS_CSV = DATA_DIR / "keywords_100.csv"

# Brand & Primary Store Details
BRAND_NAME = "BAGONSA"
STORE_URL = "https://bagonsales.shop/"
STORE_TITLE = "BAGONSA | Handcrafted Full-Grain Leather Goods & Artisanal Accessories"
STORE_DESCRIPTION = (
    "Discover BAGONSA's 100% authentic full-grain leather backpacks, vintage bomber "
    "jackets, croco-embossed handbags, rugged travel duffels, and custom boots. "
    "Handcrafted with solid brass hardware, YKK zippers, and Express 3-5 day DHL delivery."
)
TAGLINE = "Authentic Full-Grain & Top-Grain Leather Goods Handcrafted for a Lifetime"
SHIPPING_PROMISE = "Express Worldwide DHL Shipping (3–5 business days to USA, Canada, UK, and EU)"
SUPPORT_EMAIL = "support@bagonsales.shop"
CURRENCY = "USD"

# Product Silo Category Definitions & Deep-Link Mappings
SILO_CATEGORIES = {
    "leather-backpacks": {
        "id": "leather-backpacks",
        "name": "Leather Backpacks & Laptop Bags",
        "short_name": "Backpacks & Laptop Bags",
        "canonical_path": "collections/leather-backpacks",
        "target_url": "https://bagonsales.shop/collections/leather-backpacks",
        "description": "Ergonomic, padded full-grain leather backpacks and minimalist commuter rucksacks engineered for 13-16 inch laptops.",
        "icon": "🎒",
    },
    "leather-jackets": {
        "id": "leather-jackets",
        "name": "Vintage Bomber & Biker Leather Jackets",
        "short_name": "Leather Jackets",
        "canonical_path": "collections/leather-jackets",
        "target_url": "https://bagonsales.shop/collections/leather-jackets",
        "description": "Hand-stitched vintage bomber, cafe racer, and biker jackets crafted from rugged full-grain cowhide and supple lambskin.",
        "icon": "🧥",
    },
    "handbags-totes": {
        "id": "handbags-totes",
        "name": "Croco-Embossed Handbags & Luxury Totes",
        "short_name": "Handbags & Totes",
        "canonical_path": "collections/leather-handbags",
        "target_url": "https://bagonsales.shop/collections/leather-handbags",
        "description": "Exquisite croco-embossed structured handbags, luxury suede totes, and versatile crossbody satchels featuring solid brass hardware.",
        "icon": "👜",
    },
    "travel-duffels": {
        "id": "travel-duffels",
        "name": "Full-Grain Travel Duffels & Briefcases",
        "short_name": "Travel Duffels & Briefcases",
        "canonical_path": "collections/leather-travel-bags",
        "target_url": "https://bagonsales.shop/collections/leather-travel-bags",
        "description": "TSA overhead compliant weekend travel duffels, gym holdalls, and executive laptop briefcases built with reinforced YKK brass zippers.",
        "icon": "🧳",
    },
    "leather-footwear": {
        "id": "leather-footwear",
        "name": "Handcrafted Leather Boots & Footwear",
        "short_name": "Boots & Footwear",
        "canonical_path": "collections/leather-footwear",
        "target_url": "https://bagonsales.shop/collections/leather-footwear",
        "description": "Artisanal Goodyear-welted full-grain leather dress boots, rugged chelsea boots, and custom-fitted dress shoes built for resolute durability.",
        "icon": "👞",
    },
}

# GitHub Configuration for Pages and Parasite Colab Notebooks
GITHUB_USER = os.getenv("GITHUB_USER", "simokhi76-arch")
GITHUB_REPO = os.getenv("GITHUB_REPO", "bagonsa-seo-engine")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")

# GitHub Pages Static Site Root
GITHUB_PAGES_BASE_URL = os.getenv(
    "GITHUB_PAGES_BASE_URL",
    f"https://{GITHUB_USER}.github.io/{GITHUB_REPO}/"
).rstrip("/") + "/"

# Google Colab Parasite Root URL
COLAB_BASE_URL = (
    f"https://colab.research.google.com/github/{GITHUB_USER}/{GITHUB_REPO}/blob/{GITHUB_BRANCH}/dist_colab/"
)

# Google Cloud Storage (GCS) Configuration
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "bagonsa-seo-pages")
GCS_PUBLIC_BASE_URL = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/"

# Google Indexing API Configuration
SERVICE_ACCOUNT_KEY_PATH = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    str(BASE_DIR / "service_account.json")
)
INDEXING_BATCH_SIZE = int(os.getenv("INDEXING_BATCH_SIZE", "50"))
INDEXING_RATE_LIMIT_DELAY = float(os.getenv("INDEXING_RATE_LIMIT_DELAY", "1.0"))  # Seconds between requests
