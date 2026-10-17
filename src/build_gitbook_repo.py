"""
GitBook Parasite SEO Engine Builder for BAGONSA.
Compiles a complete, standard GitBook documentation structure in dist_gitbook/
including README.md, SUMMARY.md navigation, .gitbook.yaml, and 100 individual
Markdown specification guides organized across 5 product category folders.
"""

import csv
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure parent directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from src.content_matrix import get_page_content

DIST_GITBOOK_DIR = config.BASE_DIR / "dist_gitbook"


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


def render_guide_markdown(item: Dict[str, Any], content: Dict[str, Any]) -> str:
    """Renders a comprehensive, SEO-optimized GitBook Markdown article."""
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

    # Specs table
    specs_lines = [
        "| Specification Parameter | Artisanal Build Standard | Functional Advantage |",
        "| :--- | :--- | :--- |",
    ]
    for spec in content["technical_specs"]:
        specs_lines.append(f"| **{spec['spec']}** | {spec['value']} | {spec['benefit']} |")
    specs_table = "\n".join(specs_lines)

    # Comparison table
    comp = content["comparison_table"]
    comp_lines = [
        "| Engineering Parameter | BAGONSA Handcrafted Full-Grain | Standard Split Leather | Synthetic Faux / PU Plastic |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for row in comp["rows"]:
        comp_lines.append(
            f"| **{row['parameter']}** | **✓ {row['bagonsa']}** | ✕ {row['split']} | ✕ {row['faux']} |"
        )
    comp_table = "\n".join(comp_lines)

    # Care steps
    care = content["care_guide"]
    care_steps = "\n".join([f"{i}. {s}" for i, s in enumerate(care["steps"], start=1)])

    # FAQs
    faq_lines = []
    for faq in content["faqs"]:
        faq_lines.append(f"### Q: {faq['question']}\n\n**A:** {faq['answer']}\n")
    faq_section = "\n".join(faq_lines)

    # Reviews
    review_lines = []
    for r in content["reviews"]:
        review_lines.append(
            f"* ★ **{r['rating']}/5.0** — **\"{r['title']}\"** by {r['author']} ({r['location']})\n  > \"{r['review']}\"\n"
        )
    review_section = "\n".join(review_lines)

    md = f"""# {kw}

> **Category:** {silo_name} | **Price Tier:** {price} | **Verified Rating:** ★ {rating}/5.0 ({reviews_count} reviews)  
> **Buyer Focus:** `{buyer_mod}` | **Worldwide Delivery:** Express 3–5 Business Day DHL to USA, Canada, UK, and EU

* 🛒 **Direct Workshop Ordering:** [Explore on BAGONSA Official Store]({target_url})
* 🌐 **Primary Web Specification:** [Interactive GitHub Pages Guide]({html_canonical})
* 📓 **Google Colab Notebook:** [Open in Google Colab]({colab_canonical})

---

## 1. Architectural Overview & Material Provenance

**Design Philosophy:** {content['hero_hook']}

{content['hero_narrative']}

### Key Artisanal Benchmarks:
* **100% Authentic Full-Grain Leather:** Cut from the dense topmost dermal grain, providing unparalleled tear resistance and developing a rich natural patina.
* **Solid Cast Brass Hardware:** Solid brass buckles, rivets, and D-rings that never snap or corrode.
* **Heavy-Gauge YKK Zippers:** Continuous heavy-duty brass coil closures engineered for decades of smooth operation.
* **Express DHL Worldwide Delivery:** Direct artisan workshop dispatch arriving in 3–5 business days to the USA, Canada, UK, and EU.

---

## 2. Technical Specifications Matrix

{specs_table}

---

## 3. Material Benchmark: Full-Grain vs Commercial Alternatives

{comp['description']}

{comp_table}

---

## 4. Leather Care & Longevity Protocol

**Care Routine:** {care['philosophy']}  
**Recommended Frequency:** {care['frequency']}

### Maintenance Steps:
{care_steps}

---

## 5. Frequently Asked Buyer Questions

{faq_section}

---

## 6. Verified Customer Feedback

{review_section}

---

## Direct Workshop Access

To order your handcrafted piece with custom sizing, monogramming, and Express DHL delivery:

👉 **[Order {kw} Directly at BAGONSA Official Store]({target_url})**

*BAGONSA Artisanal Leathercraft. Reference: `BG-SPEC-{slug[:16].upper()}`*
"""
    return md


def generate_gitbook_summary(keywords: List[Dict[str, Any]]) -> str:
    """Generates SUMMARY.md navigation file for GitBook table of contents."""
    silos_grouped: Dict[str, List[Dict[str, Any]]] = {}
    for kw in keywords:
        s = kw["silo_category"]
        if s not in silos_grouped:
            silos_grouped[s] = []
        silos_grouped[s].append(kw)

    summary_lines = [
        "# Table of contents",
        "",
        "* [Introduction](README.md)",
        "* [Material Benchmark & Full-Grain Standards](material-standards.md)",
        "* [Artisanal Leather Care Protocol](leather-care.md)",
        "",
        "## Product Specification Directory",
        "",
    ]

    for silo_key, items in silos_grouped.items():
        silo_info = config.SILO_CATEGORIES.get(silo_key, {})
        silo_name = silo_info.get("name", silo_key)
        summary_lines.append(f"### {silo_name}")
        summary_lines.append("")
        for item in items:
            summary_lines.append(f"* [{item['keyword']}]({silo_key}/{item['slug']}.md)")
        summary_lines.append("")

    return "\n".join(summary_lines)


def generate_gitbook_readme() -> str:
    """Generates the main README.md introduction for GitBook."""
    return f"""# BAGONSA Artisanal Full-Grain Leather Master Specification Guide

Welcome to the **BAGONSA** technical documentation portal. This open reference architecture contains detailed material benchmarks, engineering specifications, and buyer guides for 100 handcrafted full-grain leather goods.

* 🌐 **Official Workshop Store:** [{config.STORE_URL}]({config.STORE_URL})
* 📚 **Interactive Web Hub:** [https://simokhi76-arch.github.io/bagonsa-leather/](https://simokhi76-arch.github.io/bagonsa-leather/)
* 📓 **Google Colab Directory:** [100 Cloud Colab Notebooks](https://simokhi76-arch.github.io/bagonsa-leather/colab-directory.html)
* 🚀 **Hugging Face Space:** [Interactive Leather Finder](https://huggingface.co/spaces)

---

## 1. Product Silo Categories

Explore all 100 complete buyer specifications across 5 artisanal product silos:

1. **🎒 Leather Backpacks & Laptop Bags (20 Guides):** Ergonomic commute rucksacks with neoprene laptop compartments (fits 14–16" MacBooks).
2. **🧥 Vintage Bomber & Biker Leather Jackets (20 Guides):** 1.2mm drum-dyed steerhide/lambskin with bi-swing action backs and quilted thermal linings.
3. **👜 Croco-Embossed Handbags & Totes (20 Guides):** Architectural structured totes with water-resistant micro-suede interiors and solid brass feet.
4. **🧳 Full-Grain Travel Duffels & Briefcases (20 Guides):** TSA overhead carry-on compliant 45L/55L luggage with ventilated shoe compartments.
5. **👞 Handcrafted Leather Boots & Footwear (20 Guides):** Resolable Goodyear welt & stitchdown boots with Vibram commando lug outsoles.

---

## 2. The BAGONSA Quality Standard

Every piece crafted by BAGONSA adheres to resolute leathercraft tolerances:
* **100% Authentic Full-Grain Leather:** Retaining natural dermal fibers for maximum durability and organic amber patina.
* **Solid Brass Hardware:** Heavy cast buckles, rivets, and D-rings that never snap under tension.
* **Industrial YKK Metal Zippers:** Smooth, jam-resistant dual-direction sliders tested for 50,000+ continuous pulls.
* **Express Worldwide DHL Delivery:** Direct workshop fulfillment reaching the USA, Canada, UK, and EU within 3 to 5 business days.

---

👉 **[Browse Full Collection at BAGONSA Official Workshop Store]({config.STORE_URL})**
"""


def generate_material_standards() -> str:
    """Generates material-standards.md for GitBook."""
    comp = get_page_content({"keyword": "BAGONSA Full Grain", "silo_category": "leather-backpacks"})["comparison_table"]
    rows = []
    for r in comp["rows"]:
        rows.append(f"| **{r['parameter']}** | **✓ {r['bagonsa']}** | ✕ {r['split']} | ✕ {r['faux']} |")
    rows_md = "\n".join(rows)

    return f"""# Material Integrity: Full-Grain vs Commercial Leather

{comp['description']}

| Engineering Parameter | BAGONSA Handcrafted Full-Grain | Standard Commercial Split Leather | Synthetic Faux / PU Plastic |
| :--- | :--- | :--- | :--- |
{rows_md}

---

## Understanding Leather Grades

* **Full-Grain Leather (BAGONSA Standard):** The highest grade of leather available. It preserves the natural grain and collagen fibers, making it virtually indestructible. Over time, it absorbs natural oils to develop a rich, lustrous patina.
* **Split / "Genuine" Leather:** The bottom split layer of animal hide that has had artificial grain embossed and painted with synthetic polymers. Lacks structural strength and breaks down within 1–2 years.
* **Faux / PU Leather:** 100% petrochemical polyurethane on polyester backing. Delaminates, cracks, and produces non-biodegradable waste.

*Visit BAGONSA Workshop: [https://bagonsales.shop/](https://bagonsales.shop/)*
"""


def generate_leather_care() -> str:
    """Generates leather-care.md for GitBook."""
    return f"""# Artisanal Leather Care & Maintenance Protocol

To preserve the natural beauty, tensile strength, and organic patina of your BAGONSA full-grain leather goods for decades, follow this standardized care protocol.

## Step-by-Step Care Routine

1. **Dust Down:** Use a soft genuine horsehair brush to remove surface grit from seams and leather crevices.
2. **Gentle Cleaning:** Wipe the hide with a slightly dampened microfiber cloth (use pH-balanced leather cleaner only for deep grime).
3. **Nutrient Conditioning:** Massage a dime-sized dollop of all-natural beeswax and lanolin conditioner in circular motions.
4. **Rest & Absorption:** Allow the oils to penetrate the grain for 30 minutes in a well-ventilated indoor space away from direct heat.
5. **Buff to Luster:** Vigorously buff with a clean horsehair brush to reveal an organic satin luster.

## Storage Best Practices
* Store your leather bags and jackets in breathable cotton dust bags (never seal in airtight plastic).
* Stuff travel duffels and totes with plain craft paper to maintain architectural silhouette when not in use.
* Keep in a climate-controlled room away from damp basements and prolonged direct radiator heat.

*Visit BAGONSA Workshop: [https://bagonsales.shop/](https://bagonsales.shop/)*
"""


def generate_gitbook_yaml() -> str:
    """Generates .gitbook.yaml configuration."""
    return """root: ./
structure:
  readme: README.md
  summary: SUMMARY.md
"""


def build_gitbook_bundle():
    """Builds the complete GitBook documentation bundle inside dist_gitbook/."""
    print("=" * 65)
    print("BAGONSA GITBOOK PARASITE SEO ENGINE BUILDER")
    print("=" * 65)

    keywords = load_keywords()
    print(f"Loaded {len(keywords)} keywords from {config.KEYWORDS_CSV}")

    DIST_GITBOOK_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Main README.md
    with open(DIST_GITBOOK_DIR / "README.md", "w", encoding="utf-8") as f:
        f.write(generate_gitbook_readme())
    print("  [OK] Generated GitBook README.md")

    # 2. SUMMARY.md
    with open(DIST_GITBOOK_DIR / "SUMMARY.md", "w", encoding="utf-8") as f:
        f.write(generate_gitbook_summary(keywords))
    print("  [OK] Generated GitBook SUMMARY.md (Table of Contents)")

    # 3. material-standards.md
    with open(DIST_GITBOOK_DIR / "material-standards.md", "w", encoding="utf-8") as f:
        f.write(generate_material_standards())
    print("  [OK] Generated material-standards.md")

    # 4. leather-care.md
    with open(DIST_GITBOOK_DIR / "leather-care.md", "w", encoding="utf-8") as f:
        f.write(generate_leather_care())
    print("  [OK] Generated leather-care.md")

    # 5. .gitbook.yaml
    with open(DIST_GITBOOK_DIR / ".gitbook.yaml", "w", encoding="utf-8") as f:
        f.write(generate_gitbook_yaml())
    print("  [OK] Generated .gitbook.yaml")

    # 6. Generate 100 individual category Markdown files
    for i, item in enumerate(keywords, start=1):
        silo = item["silo_category"]
        silo_dir = DIST_GITBOOK_DIR / silo
        silo_dir.mkdir(parents=True, exist_ok=True)

        content = get_page_content(item)
        md_text = render_guide_markdown(item, content)

        guide_file = silo_dir / f"{item['slug']}.md"
        with open(guide_file, "w", encoding="utf-8") as f:
            f.write(md_text)

        if i % 25 == 0 or i == len(keywords):
            print(f"  [OK] Generated {i}/{len(keywords)} GitBook guides: {guide_file.name}")

    print("=" * 65)
    print(f"SUCCESS: Compiled 100 GitBook guides + navigation into {DIST_GITBOOK_DIR}")
    print("=" * 65)


if __name__ == "__main__":
    build_gitbook_bundle()
