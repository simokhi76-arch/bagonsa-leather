"""
Google Colab Parasite Notebook Generator for BAGONSA.
Builds 100 SEO-optimized, valid JSON-formatted .ipynb (nbformat v4) notebooks
populated purely with rich Markdown cells (zero executable code cells to prevent
Google abuse flags) hosted at colab.research.google.com/github/...
"""

import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure parent directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from src.content_matrix import get_page_content


def load_keywords() -> List[Dict[str, Any]]:
    """Loads all keyword records from data/keywords_100.csv."""
    keywords = []
    with open(config.KEYWORDS_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["rating_value"] = float(row["rating_value"])
            row["review_count"] = int(row["review_count"])
            keywords.append(row)
    return keywords


def create_markdown_cell(lines: List[str]) -> Dict[str, Any]:
    """Wraps lines of text into a valid Jupyter Markdown cell dict."""
    source_lines = [line + "\n" for line in lines[:-1]] + [lines[-1]] if lines else []
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source_lines,
    }


def generate_colab_notebook(item: Dict[str, Any], content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compiles a complete Jupyter notebook (nbformat v4) consisting strictly
    of rich Markdown cells for the given keyword.
    """
    kw = item["keyword"]
    slug = item["slug"]
    silo_key = item["silo_category"]
    silo_info = config.SILO_CATEGORIES.get(silo_key, {})
    silo_name = silo_info.get("name", "Leather Goods")
    target_url = item["target_store_url"]
    price = item["price_range"]
    rating = item["rating_value"]
    reviews_count = item["review_count"]
    buyer_mod = item["buyer_modifier"]

    html_canonical = f"{config.GITHUB_PAGES_BASE_URL}{slug}.html"
    colab_canonical = f"{config.COLAB_BASE_URL}{slug}.ipynb"

    cells = []

    # Cell 1: Colab Badge, Title & Navigation Links
    cell1_lines = [
        f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]({colab_canonical})",
        "",
        f"# BAGONSA Technical Specification: {kw}",
        "",
        f"> **Category:** {silo_name} | **Price Tier:** {price} | **Verified Rating:** ★ {rating}/5.0 ({reviews_count} reviews)",
        f"> **Buyer Focus:** `{buyer_mod}` | **Worldwide Delivery:** Express 3–5 Business Day DHL to USA, Canada, UK, and EU",
        "",
        f"🔗 **Primary Web Document:** [Read the Full Interactive Guide on GitHub Pages]({html_canonical})  ",
        f"🛒 **Direct Workshop Ordering:** [Explore BAGONSA Official Workshop Collection]({target_url})  ",
        f"🌐 **Brand Domain:** [{config.STORE_URL}]({config.STORE_URL})",
        "---",
    ]
    cells.append(create_markdown_cell(cell1_lines))

    # Cell 2: Architectural Overview & Material Sourcing
    cell2_lines = [
        "## 1. Material Architecture & Hide Provenance",
        "",
        f"**Design Philosophy:** {content['hero_hook']}",
        "",
        content["hero_narrative"],
        "",
        "### Key Artisanal Benchmarks:",
        "- **100% Authentic Full-Grain Leather:** Preserves the dense natural dermal grain, resisting tearing and peeling.",
        "- **Solid Cast Brass Hardware:** Heavy-duty buckles, D-rings, and rivets that never rust or snap under load.",
        "- **Industrial YKK Metal Zippers:** Smooth, jam-resistant dual-direction sliders tested for 50,000+ continuous pulls.",
        "- **Express DHL Worldwide Delivery:** Direct from artisan workshop to USA, Canada, UK, and EU in 3 to 5 business days.",
        "- **Direct-to-Consumer Workshop Pricing:** Heirloom leathercraft without middleman designer markups.",
    ]
    cells.append(create_markdown_cell(cell2_lines))

    # Cell 3: Technical Specifications Table (Markdown Table)
    cell3_lines = [
        "## 2. Engineering & Technical Specifications",
        "",
        "| Specification Parameter | Artisanal Build Standard | Functional Benefit |",
        "| :--- | :--- | :--- |",
    ]
    for spec in content["technical_specs"]:
        cell3_lines.append(f"| **{spec['spec']}** | {spec['value']} | {spec['benefit']} |")
    cells.append(create_markdown_cell(cell3_lines))

    # Cell 4: Material Comparison Table (Markdown Table)
    comp = content["comparison_table"]
    cell4_lines = [
        f"## 3. Material Benchmark: {comp['title']}",
        "",
        comp["description"],
        "",
        "| Engineering Parameter | BAGONSA Handcrafted Full-Grain | Standard Split Leather | Synthetic Faux / PU Leather |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for row in comp["rows"]:
        cell4_lines.append(
            f"| **{row['parameter']}** | **✓ {row['bagonsa']}** | ✕ {row['split']} | ✕ {row['faux']} |"
        )
    cells.append(create_markdown_cell(cell4_lines))

    # Cell 5: Leather Care & Maintenance Protocol
    care = content["care_guide"]
    cell5_lines = [
        f"## 4. {care['title']}",
        "",
        f"**Routine:** {care['philosophy']}  ",
        f"**Recommended Frequency:** {care['frequency']}",
        "",
        "### Actionable Maintenance Steps:",
    ]
    for i, step in enumerate(care["steps"], start=1):
        cell5_lines.append(f"{i}. {step}")
    cells.append(create_markdown_cell(cell5_lines))

    # Cell 6: Dynamic FAQs
    cell6_lines = [
        "## 5. Frequently Asked Buyer Questions",
        "",
    ]
    for faq in content["faqs"]:
        cell6_lines.append(f"### Q: {faq['question']}")
        cell6_lines.append(f"**A:** {faq['answer']}")
        cell6_lines.append("")
    cells.append(create_markdown_cell(cell6_lines))

    # Cell 7: Verified Reviews & Direct Workshop Link
    cell7_lines = [
        "## 6. Verified Buyer Experiences & Workshop Access",
        "",
    ]
    for r in content["reviews"]:
        cell7_lines.append(
            f"★ **{r['rating']}/5.0** — *\"{r['title']}\"* by **{r['author']}** ({r['location']})  "
        )
        cell7_lines.append(f"> \"{r['review']}\"")
        cell7_lines.append("")

    cell7_lines.extend([
        "---",
        "### How to Order Your Piece:",
        f"1. Visit the official product page: [{target_url}]({target_url})",
        "2. Select your leather finish, size, and personalization options.",
        "3. Complete checkout with secure encrypted payment (Credit Cards, PayPal, Apple Pay).",
        "4. Your order is handcrafted and dispatched via Express DHL with step-by-step tracking in 3–5 days.",
        "",
        f"👉 **[Click Here to Explore {kw} on BAGONSA Official Store]({target_url})**",
        "",
        f"*Reference Document ID: BAGONSA-SPEC-{slug[:16].upper()} | Copyright 2026 BAGONSA. All rights reserved.*",
    ])
    cells.append(create_markdown_cell(cell7_lines))

    notebook = {
        "cells": cells,
        "metadata": {
            "colab": {
                "name": f"{slug}.ipynb",
                "provenance": [],
                "toc_visible": True,
            },
            "kernelspec": {
                "display_name": "Python 3",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    return notebook


def main():
    """Builds 100 SEO-optimized .ipynb notebook files inside dist_colab/."""
    print("=" * 65)
    print("BAGONSA GOOGLE COLAB PARASITE NOTEBOOK COMPILER")
    print("=" * 65)

    keywords = load_keywords()
    print(f"Loaded {len(keywords)} keywords from {config.KEYWORDS_CSV}")

    config.DIST_COLAB_DIR.mkdir(parents=True, exist_ok=True)

    for i, item in enumerate(keywords, start=1):
        content = get_page_content(item)
        notebook_data = generate_colab_notebook(item, content)

        notebook_file = config.DIST_COLAB_DIR / f"{item['slug']}.ipynb"
        with open(notebook_file, "w", encoding="utf-8") as f:
            json.dump(notebook_data, f, indent=2, ensure_ascii=False)

        if i % 25 == 0 or i == len(keywords):
            print(f"  [OK] Generated {i}/{len(keywords)} Colab notebooks: {notebook_file.name}")

    print("=" * 65)
    print(f"SUCCESS: Compiled 100 Colab notebooks into {config.DIST_COLAB_DIR}")
    print("=" * 65)


if __name__ == "__main__":
    main()
