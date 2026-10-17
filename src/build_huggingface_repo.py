"""
Hugging Face Parasite SEO Builder for BAGONSA.
Compiles a complete, standalone Hugging Face Space & Dataset repository
in dist_huggingface/ featuring an interactive Gradio search app, comprehensive
YAML metadata card, and 100 buyer-intent specifications linking to bagonsales.shop.
"""

import csv
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure parent directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from src.content_matrix import get_page_content

DIST_HF_DIR = config.BASE_DIR / "dist_huggingface"


def load_keywords() -> List[Dict[str, Any]]:
    """Loads all 100 keyword records from data/keywords_100.csv."""
    keywords = []
    with open(config.KEYWORDS_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["rating_value"] = float(row["rating_value"])
            row["review_count"] = int(row["review_count"])
            keywords.append(row)
    return keywords


def generate_hf_readme(keywords: List[Dict[str, Any]]) -> str:
    """Generates a rich, SEO-optimized Hugging Face Space/Dataset README card."""
    silos_summary = {}
    for kw in keywords:
        s = kw["silo_category"]
        silos_summary[s] = silos_summary.get(s, 0) + 1

    rows_md = []
    for item in keywords:
        silo_name = config.SILO_CATEGORIES.get(item['silo_category'], {}).get('short_name', item['silo_category'])
        rows_md.append(
            f"| {item['id']} | [{item['keyword']}]({item['target_store_url']}) | `{silo_name}` | {item['price_range']} | ★ {item['rating_value']} | [Order on Store]({item['target_store_url']}) |"
        )
    table_content = "\n".join(rows_md)

    readme_content = f"""---
title: BAGONSA Handcrafted Full-Grain Leather Goods Catalog & Buyer Benchmark
emoji: 🎒
colorFrom: yellow
colorTo: red
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
tags:
  - ecommerce
  - leather-goods
  - buyer-guide
  - full-grain-leather
  - handcrafted
  - bagonsa
  - fashion
  - luxury
pretty_name: BAGONSA 100% Authentic Full-Grain Leather Directory
---

# BAGONSA Artisanal Full-Grain Leather Goods Directory & Buyer Specification Benchmark

Welcome to the official **BAGONSA** interactive product index on Hugging Face. BAGONSA specializes in **100% authentic full-grain and top-grain leather goods**, handcrafted with solid brass hardware, YKK zippers, custom-tailored sizing, and **Express Worldwide DHL Shipping (3–5 business days to USA, Canada, UK, and EU)**.

* 🌐 **Official Workshop Store:** [{config.STORE_URL}]({config.STORE_URL})
* 📚 **GitHub Pages Master Directory:** [https://simokhi76-arch.github.io/bagonsa-leather/](https://simokhi76-arch.github.io/bagonsa-leather/)
* 📓 **Google Colab Notebooks:** [Google Colab Directory](https://simokhi76-arch.github.io/bagonsa-leather/colab-directory.html)

---

## 1. Product Catalog Overview (100 Verified Buyer Specifications)

This database indexes 100 high-converting long-tail buyer specifications across 5 core silos:
1. **Leather Backpacks & Laptop Bags (20 items):** Padded neoprene sleeves for 14-16" MacBooks, ergonomic weight distribution.
2. **Vintage Bomber & Biker Leather Jackets (20 items):** 1.2mm drum-dyed steerhide/lambskin, bi-swing action backs, quilted satin lining.
3. **Croco-Embossed Handbags & Luxury Totes (20 items):** Deep-texture bovine croco, water-resistant micro-suede interiors, 5-layer electroplated solid brass feet.
4. **Full-Grain Travel Duffels & Briefcases (20 items):** TSA overhead carry-on compliant (45L/55L), isolated ventilated shoe holds.
5. **Handcrafted Leather Boots & Footwear (20 items):** Goodyear welted & stitchdown resolable foundations, Vibram commando lug outsoles.

---

## 2. Complete Material Benchmark Table

| ID | Product Specification | Product Category | Price Tier | Verified Rating | Workshop Access Link |
| :---: | :--- | :--- | :---: | :---: | :--- |
{table_content}

---

## 3. Artisanal Quality Benchmarks vs Commercial Alternatives

| Parameter | BAGONSA Handcrafted Full-Grain | Standard Commercial Split Leather | Synthetic Faux / PU Plastic |
| :--- | :--- | :--- | :--- |
| **Material Layer** | Outermost tight dermal layer intact | Discarded inner flesh coated in vinyl paint | 100% polyurethane plastic film on fabric |
| **Durability Lifespan** | **15 to 30+ Years** (develops rich patina) | 1 to 2 Years (cracks and splits at folds) | 6 to 18 Months (peels and tears easily) |
| **Hardware Standard** | Solid cast brass rivets & buckles | Weak zinc alloy / pot metal | Hollow plastic or stamped tin |
| **Zippers** | Heavy-duty YKK continuous brass coil | Cheap unbranded nylon sliders | Plastic tooth closures |
| **Global Shipping** | **Express DHL 3–5 Days Worldwide** | Slow standard postal transit | Drop-shipped economy mail |

---

## 4. Ordering & Worldwide Dispatch

All pieces are available directly from the artisan workshop at honest direct-to-consumer pricing:
* **USA / Canada:** Express DHL delivery within 3–5 business days.
* **UK / European Union:** Express DHL delivery with all VAT duties accommodated.
* **Store URL:** [{config.STORE_URL}]({config.STORE_URL})

*Dataset curated by BAGONSA Technical Architecture Team. Copyright 2026 BAGONSA. All rights reserved.*
"""
    return readme_content


def generate_gradio_app() -> str:
    """Generates a standalone, beautiful Gradio web app for Hugging Face Spaces."""
    return '''import gradio as gr
import pandas as pd
from pathlib import Path

# Load catalog data
csv_path = Path(__file__).resolve().parent / "keywords_100.csv"
if not csv_path.exists():
    csv_path = Path(__file__).resolve().parent / "data" / "keywords_100.csv"

df = pd.read_csv(csv_path)

CATEGORY_MAP = {
    "All Categories": "All",
    "Backpacks & Laptop Bags": "leather-backpacks",
    "Leather Jackets": "leather-jackets",
    "Handbags & Totes": "handbags-totes",
    "Travel Duffels & Briefcases": "travel-duffels",
    "Boots & Footwear": "leather-footwear",
}

def filter_catalog(search_query, selected_category):
    filtered = df.copy()
    
    # Category filter
    cat_code = CATEGORY_MAP.get(selected_category, "All")
    if cat_code != "All":
        filtered = filtered[filtered["silo_category"] == cat_code]
        
    # Search query filter
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        filtered = filtered[
            filtered["keyword"].str.lower().str.contains(q) |
            filtered["buyer_modifier"].str.lower().str.contains(q)
        ]
        
    # Format display table
    display_df = pd.DataFrame({
        "ID": filtered["id"],
        "Product Title": filtered["keyword"],
        "Focus Feature": filtered["buyer_modifier"],
        "Price Range": filtered["price_range"],
        "Rating": filtered["rating_value"].apply(lambda r: f"★ {r}/5.0"),
        "Store Link": filtered["target_store_url"],
    })
    
    status_text = f"Showing {len(display_df)} handcrafted leather specifications."
    return display_df, status_text

custom_css = """
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
.gradio-container { max-width: 1100px !important; margin: 0 auto !important; }
h1 { color: #8b4513 !important; font-weight: 800 !important; }
"""

with gr.Blocks(css=custom_css, title="BAGONSA Full-Grain Leather Goods Catalog") as demo:
    gr.Markdown(
        """
        # 🎒 BAGONSA Artisanal Full-Grain Leather Catalog & Buyer Guide
        ### Handcrafted Leather Backpacks, Vintage Jackets, Handbags, Travel Duffels & Boots
        **100% Authentic Full-Grain Leather | Solid Brass Hardware | Heavy-Duty YKK Zippers | Express 3–5 Day DHL Delivery**
        
        *Official Workshop Store:* [https://bagonsales.shop/](https://bagonsales.shop/)  
        *GitHub Pages Web Directory:* [https://simokhi76-arch.github.io/bagonsa-leather/](https://simokhi76-arch.github.io/bagonsa-leather/)
        """
    )
    
    with gr.Row():
        search_input = gr.Textbox(
            label="Search by Product Name or Feature",
            placeholder="e.g. Laptop Backpack, Vintage Bomber, Croco, Travel Duffel, Boots...",
            scale=3,
        )
        category_dropdown = gr.Dropdown(
            choices=list(CATEGORY_MAP.keys()),
            value="All Categories",
            label="Filter by Product Category",
            scale=2,
        )
    
    status_output = gr.Markdown("Showing 100 handcrafted leather specifications.")
    table_output = gr.Dataframe(
        headers=["ID", "Product Title", "Focus Feature", "Price Range", "Rating", "Store Link"],
        datatype=["number", "str", "str", "str", "str", "str"],
        interactive=False,
    )
    
    search_input.change(filter_catalog, inputs=[search_input, category_dropdown], outputs=[table_output, status_output])
    category_dropdown.change(filter_catalog, inputs=[search_input, category_dropdown], outputs=[table_output, status_output])
    demo.load(filter_catalog, inputs=[search_input, category_dropdown], outputs=[table_output, status_output])
    
    gr.Markdown(
        """
        ---
        ### Why Choose BAGONSA Full-Grain Leather?
        * **100% Genuine Top & Full-Grain Hides:** We never use cheap bonded, split, or synthetic PU leather. Our hides breathe and develop a lustrous patina over decades.
        * **Heirloom Hardware:** Solid antiqued brass buckles and reinforced rivets that withstand 100+ lbs of tension.
        * **Express DHL Shipping:** Dispatched straight from our artisan workshop to the USA, Canada, UK, and EU within 3 to 5 business days.
        * **Explore Store:** [https://bagonsales.shop/](https://bagonsales.shop/)
        """
    )

if __name__ == "__main__":
    demo.launch()
'''


def build_huggingface_bundle():
    """Builds the complete Hugging Face Space repository inside dist_huggingface/."""
    print("=" * 65)
    print("BAGONSA HUGGING FACE PARASITE SEO ENGINE BUILDER")
    print("=" * 65)

    keywords = load_keywords()
    print(f"Loaded {len(keywords)} keywords from {config.KEYWORDS_CSV}")

    DIST_HF_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Generate README.md
    readme_content = generate_hf_readme(keywords)
    readme_path = DIST_HF_DIR / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"  [OK] Generated Hugging Face Space/Dataset README: {readme_path.name}")

    # 2. Generate Gradio app.py
    app_content = generate_gradio_app()
    app_path = DIST_HF_DIR / "app.py"
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_content)
    print(f"  [OK] Generated Interactive Gradio App: {app_path.name}")

    # 3. Copy keywords_100.csv
    csv_dest = DIST_HF_DIR / "keywords_100.csv"
    with open(config.KEYWORDS_CSV, "r", encoding="utf-8") as src_f, open(csv_dest, "w", encoding="utf-8") as dst_f:
        dst_f.write(src_f.read())
    print(f"  [OK] Bundled Dataset CSV: {csv_dest.name}")

    # 4. Generate requirements.txt for Hugging Face Spaces
    hf_reqs = "gradio>=4.44.0\npandas>=2.0.0\n"
    reqs_path = DIST_HF_DIR / "requirements.txt"
    with open(reqs_path, "w", encoding="utf-8") as f:
        f.write(hf_reqs)
    print(f"  [OK] Generated Space Requirements: {reqs_path.name}")

    print("=" * 65)
    print(f"SUCCESS: Hugging Face Parasite bundle created at {DIST_HF_DIR}")
    print("=" * 65)


if __name__ == "__main__":
    build_huggingface_bundle()
