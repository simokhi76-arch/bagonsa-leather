"""
HTML5 Page Builder & SEO Schema Compiler for BAGONSA.
Generates 100 mobile-first, high-PageSpeed HTML5 buyer guides,
plus index.html directory hub, sitemap.xml, and robots.txt.
Injects Dual JSON-LD (Product + FAQPage) and closed-loop silo internal links.
"""

import csv
import json
import os
import sys
from datetime import datetime, timezone
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


def get_internal_links(
    current_item: Dict[str, Any],
    all_items: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Selects 5 related items within the same Silo and 2 cross-silo items
    to create a closed crawl loop for search engine spiders.
    """
    current_id = current_item["id"]
    current_silo = current_item["silo_category"]

    # Same silo candidates (excluding current)
    same_silo = [item for item in all_items if item["silo_category"] == current_silo and item["id"] != current_id]
    # Rotate deterministically based on ID
    offset = current_id % len(same_silo)
    same_silo_selected = (same_silo[offset:] + same_silo[:offset])[:5]

    # Cross silo candidates
    other_silos = [item for item in all_items if item["silo_category"] != current_silo]
    cross_offset = (current_id * 3) % len(other_silos)
    cross_silo_selected = (other_silos[cross_offset:] + other_silos[:cross_offset])[:2]

    return {
        "same_silo": same_silo_selected,
        "cross_silo": cross_silo_selected,
    }


def render_html_page(
    item: Dict[str, Any],
    content: Dict[str, Any],
    internal_links: Dict[str, List[Dict[str, Any]]]
) -> str:
    """Renders a complete, standalone, semantic HTML5 page with dual JSON-LD schemas."""
    kw = item["keyword"]
    slug = item["slug"]
    silo_key = item["silo_category"]
    silo_info = config.SILO_CATEGORIES.get(silo_key, {})
    silo_name = silo_info.get("name", "Leather Goods")
    silo_url = silo_info.get("target_url", config.STORE_URL)
    target_url = item["target_store_url"]
    price_range = item["price_range"]
    rating_val = item["rating_value"]
    review_cnt = item["review_count"]
    buyer_mod = item["buyer_modifier"]

    # Extract numerical price for Schema.org
    raw_price = price_range.split("-")[0].replace("$", "").strip()
    try:
        numeric_price = f"{float(raw_price):.2f}"
    except ValueError:
        numeric_price = "139.00"

    canonical_url = f"{config.GITHUB_PAGES_BASE_URL}{slug}.html"
    colab_url = f"{config.COLAB_BASE_URL}{slug}.ipynb"

    meta_title = f"{kw} | Handcrafted Full-Grain Leather | BAGONSA"
    meta_desc = (
        f"In-depth guide & technical review of {kw}. Handcrafted from 100% full-grain leather, "
        f"solid brass hardware, and heavy-duty YKK zippers. Express 3-5 day DHL shipping worldwide."
    )

    # 1. Product JSON-LD Schema
    product_schema = {
        "@context": "https://schema.org/",
        "@type": "Product",
        "name": f"BAGONSA {kw}",
        "description": meta_desc,
        "sku": f"BAGONSA-{slug[:18].upper()}",
        "mpn": f"BG-{item['id']:04d}",
        "brand": {
            "@type": "Brand",
            "name": config.BRAND_NAME
        },
        "offers": {
            "@type": "Offer",
            "url": target_url,
            "priceCurrency": config.CURRENCY,
            "price": numeric_price,
            "priceValidUntil": "2027-12-31",
            "itemCondition": "https://schema.org/NewCondition",
            "availability": "https://schema.org/InStock",
            "seller": {
                "@type": "Organization",
                "name": config.BRAND_NAME,
                "url": config.STORE_URL
            }
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": str(rating_val),
            "reviewCount": str(review_cnt),
            "bestRating": "5",
            "worstRating": "1"
        },
        "review": [
            {
                "@type": "Review",
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": str(r["rating"]),
                    "bestRating": "5"
                },
                "author": {
                    "@type": "Person",
                    "name": r["author"]
                },
                "reviewBody": r["review"]
            }
            for r in content["reviews"][:2]
        ]
    }

    # 2. FAQPage JSON-LD Schema
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f["answer"]
                }
            }
            for f in content["faqs"]
        ]
    }

    # Render technical specifications rows
    specs_rows_html = "".join([
        f"""<tr>
            <td class="spec-name"><strong>{s['spec']}</strong></td>
            <td class="spec-value">{s['value']}</td>
            <td class="spec-benefit">{s['benefit']}</td>
        </tr>"""
        for s in content["technical_specs"]
    ])

    # Render comparison table rows
    comp_table = content["comparison_table"]
    comp_rows_html = "".join([
        f"""<tr>
            <td class="comp-param"><strong>{r['parameter']}</strong></td>
            <td class="comp-bagonsa"><span class="badge-good">✓</span> {r['bagonsa']}</td>
            <td class="comp-split"><span class="badge-bad">✕</span> {r['split']}</td>
            <td class="comp-faux"><span class="badge-bad">✕</span> {r['faux']}</td>
        </tr>"""
        for r in comp_table["rows"]
    ])

    # Render care steps
    care_guide = content["care_guide"]
    care_steps_html = "".join([
        f"<li><strong>{step.split(':')[0]}:</strong>{':'.join(step.split(':')[1:])}</li>"
        for step in care_guide["steps"]
    ])

    # Render customer reviews
    reviews_html = "".join([
        f"""<div class="review-card">
            <div class="review-header">
                <span class="review-stars">{"★" * r['rating']}</span>
                <span class="review-date">{r['date']}</span>
            </div>
            <h4 class="review-title">"{r['title']}"</h4>
            <p class="review-body">{r['review']}</p>
            <div class="review-meta">
                <span class="review-author">{r['author']}</span> • 
                <span class="review-location">{r['location']}</span> • 
                <span class="badge-verified">✓ Verified Buyer</span>
            </div>
        </div>"""
        for r in content["reviews"]
    ])

    # Render FAQs
    faqs_html = "".join([
        f"""<div class="faq-item">
            <h3 class="faq-question">{f['question']}</h3>
            <p class="faq-answer">{f['answer']}</p>
        </div>"""
        for f in content["faqs"]
    ])

    # Render Internal Links (Same Silo)
    same_silo_html = "".join([
        f"""<li>
            <a href="{link['slug']}.html" class="link-related">
                <strong>{link['keyword']}</strong>
            </a>
            <span class="link-price">{link['price_range']}</span>
        </li>"""
        for link in internal_links["same_silo"]
    ])

    # Render Internal Links (Cross Silo)
    cross_silo_html = "".join([
        f"""<li>
            <a href="{link['slug']}.html" class="link-cross">
                <strong>{link['keyword']}</strong>
            </a>
            <span class="link-cat">({config.SILO_CATEGORIES.get(link['silo_category'], {}).get('short_name', 'Leather')})</span>
        </li>"""
        for link in internal_links["cross_silo"]
    ])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meta_title}</title>
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="{canonical_url}">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    <meta name="google-site-verification" content="google9d2790f8d29dbd34.html">
    <meta name="google-site-verification" content="google9d2790f8d29dbd34">
    <meta name="google-site-verification" content="2plITmBLaHMbWEm8O0qjfrzMyH0yhIDoCL-5Exq1vmU">
    
    <!-- OpenGraph / Social Metadata -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{meta_title}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:site_name" content="{config.BRAND_NAME}">
    <meta property="og:locale" content="en_US">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{meta_title}">
    <meta name="twitter:description" content="{meta_desc}">
    
    <!-- Dual JSON-LD Structured Data (Product + FAQPage) -->
    <script type="application/ld+json">
{json.dumps(product_schema, indent=2)}
    </script>
    <script type="application/ld+json">
{json.dumps(faq_schema, indent=2)}
    </script>

    <!-- Ultra-Fast Inline CSS (PageSpeed 100/100, Zero Render Blocking) -->
    <style>
        :root {{
            --bg-canvas: #faf8f5;
            --bg-card: #ffffff;
            --text-primary: #1c1917;
            --text-secondary: #57534e;
            --text-muted: #78716c;
            --accent-leather: #8b4513;
            --accent-brass: #b45309;
            --accent-dark: #292524;
            --border-light: #e7e5e4;
            --border-accent: #d6d3d1;
            --cta-gradient: linear-gradient(135deg, #8b4513 0%, #b45309 100%);
            --cta-hover: linear-gradient(135deg, #78350f 0%, #92400e 100%);
            --font-stack: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Georgia, serif;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-canvas);
            color: var(--text-primary);
            font-family: var(--font-stack);
            font-size: 16px;
            line-height: 1.65;
            -webkit-font-smoothing: antialiased;
        }}
        header {{
            background: #ffffff;
            border-bottom: 1px solid var(--border-light);
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .header-inner {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 0 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .brand-logo {{
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: 0.15em;
            color: var(--text-primary);
            text-decoration: none;
            text-transform: uppercase;
        }}
        .brand-logo span {{ color: var(--accent-leather); }}
        .nav-links a {{
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.95rem;
            font-weight: 600;
            margin-left: 1.5rem;
            transition: color 0.2s ease;
        }}
        .nav-links a:hover {{ color: var(--accent-leather); }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 2rem 1.5rem 4rem;
        }}
        .breadcrumbs {{
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 1.5rem;
        }}
        .breadcrumbs a {{
            color: var(--text-secondary);
            text-decoration: none;
        }}
        .breadcrumbs a:hover {{ text-decoration: underline; }}
        .hero-section {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 2.5rem;
            border: 1px solid var(--border-light);
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
            margin-bottom: 2.5rem;
        }}
        .badge-silo {{
            display: inline-block;
            background: #fef3c7;
            color: #92400e;
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 0.35rem 0.75rem;
            border-radius: 9999px;
            margin-bottom: 1rem;
        }}
        .badge-mod {{
            display: inline-block;
            background: #e0f2fe;
            color: #0369a1;
            font-size: 0.8rem;
            font-weight: 700;
            padding: 0.35rem 0.75rem;
            border-radius: 9999px;
            margin-left: 0.5rem;
            margin-bottom: 1rem;
        }}
        h1 {{
            font-size: 2.25rem;
            line-height: 1.25;
            color: var(--text-primary);
            margin-bottom: 1rem;
            font-weight: 800;
        }}
        .hero-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
            align-items: center;
            font-size: 0.95rem;
            color: var(--text-secondary);
            margin-bottom: 1.75rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--border-light);
        }}
        .hero-meta .price {{
            font-weight: 800;
            font-size: 1.35rem;
            color: var(--accent-leather);
        }}
        .hero-meta .rating {{ color: #eab308; }}
        .hero-hook {{
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 1rem;
            line-height: 1.5;
        }}
        .hero-narrative {{
            font-size: 1.05rem;
            color: var(--text-secondary);
            margin-bottom: 2rem;
        }}
        .cta-box {{
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            align-items: center;
        }}
        .cta-primary {{
            display: inline-block;
            background: var(--cta-gradient);
            color: #ffffff;
            font-size: 1.1rem;
            font-weight: 700;
            text-decoration: none;
            padding: 1rem 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(139, 69, 19, 0.3);
            transition: all 0.2s ease;
        }}
        .cta-primary:hover {{
            background: var(--cta-hover);
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(139, 69, 19, 0.4);
        }}
        .btn-colab {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: #ffffff;
            color: #1e293b;
            font-size: 0.95rem;
            font-weight: 600;
            text-decoration: none;
            padding: 0.95rem 1.5rem;
            border-radius: 8px;
            border: 1px solid var(--border-accent);
            transition: all 0.2s ease;
        }}
        .btn-colab:hover {{
            background: #f1f5f9;
            border-color: #94a3b8;
        }}
        .section-card {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 2.5rem;
            border: 1px solid var(--border-light);
            margin-bottom: 2.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        }}
        h2 {{
            font-size: 1.65rem;
            color: var(--text-primary);
            margin-bottom: 1.25rem;
            position: relative;
            padding-bottom: 0.5rem;
        }}
        h2::after {{
            content: "";
            position: absolute;
            left: 0;
            bottom: 0;
            width: 48px;
            height: 3px;
            background: var(--accent-leather);
            border-radius: 2px;
        }}
        .table-responsive {{
            overflow-x: auto;
            margin-top: 1rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
        }}
        th, td {{
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-light);
        }}
        th {{
            background-color: #f8fafc;
            color: var(--text-primary);
            font-weight: 700;
        }}
        .spec-name {{ width: 25%; color: var(--text-primary); }}
        .spec-value {{ width: 40%; color: var(--accent-leather); font-weight: 600; }}
        .spec-benefit {{ width: 35%; color: var(--text-secondary); }}
        .badge-good {{ color: #16a34a; font-weight: 800; }}
        .badge-bad {{ color: #dc2626; font-weight: 800; }}
        .care-list {{
            list-style: decimal inside;
            margin-top: 1rem;
        }}
        .care-list li {{
            margin-bottom: 0.75rem;
            color: var(--text-secondary);
        }}
        .reviews-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }}
        .review-card {{
            background: #fdfcfb;
            border: 1px solid var(--border-light);
            border-radius: 8px;
            padding: 1.5rem;
        }}
        .review-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
            font-size: 0.85rem;
        }}
        .review-stars {{ color: #eab308; font-size: 1rem; }}
        .review-date {{ color: var(--text-muted); }}
        .review-title {{
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            color: var(--text-primary);
        }}
        .review-body {{
            font-size: 0.95rem;
            color: var(--text-secondary);
            margin-bottom: 1rem;
            font-style: italic;
        }}
        .review-meta {{
            font-size: 0.8rem;
            color: var(--text-muted);
        }}
        .badge-verified {{ color: #16a34a; font-weight: 600; }}
        .faq-item {{
            border-bottom: 1px solid var(--border-light);
            padding: 1.25rem 0;
        }}
        .faq-item:last-child {{ border-bottom: none; }}
        .faq-question {{
            font-size: 1.15rem;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            font-weight: 700;
        }}
        .faq-answer {{
            color: var(--text-secondary);
            font-size: 1rem;
        }}
        .links-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 1.5rem;
        }}
        .links-column ul {{
            list-style: none;
        }}
        .links-column li {{
            margin-bottom: 0.75rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid #f1f5f9;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .links-column li a {{
            color: var(--text-primary);
            text-decoration: none;
            font-size: 0.95rem;
        }}
        .links-column li a:hover {{
            color: var(--accent-leather);
            text-decoration: underline;
        }}
        .link-price {{
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--accent-brass);
        }}
        .link-cat {{
            font-size: 0.8rem;
            color: var(--text-muted);
        }}
        .banner-direct {{
            background: linear-gradient(135deg, #1c1917 0%, #292524 100%);
            color: #ffffff;
            border-radius: 12px;
            padding: 2.5rem;
            text-align: center;
            margin-bottom: 2.5rem;
        }}
        .banner-direct h3 {{
            font-size: 1.85rem;
            margin-bottom: 0.75rem;
            color: #ffffff;
        }}
        .banner-direct p {{
            color: #d6d3d1;
            max-width: 650px;
            margin: 0 auto 1.75rem;
            font-size: 1.05rem;
        }}
        footer {{
            background: #ffffff;
            border-top: 1px solid var(--border-light);
            padding: 3rem 0;
            color: var(--text-muted);
            font-size: 0.9rem;
        }}
        .footer-inner {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 0 1.5rem;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            gap: 2rem;
        }}
        .footer-col h4 {{
            color: var(--text-primary);
            margin-bottom: 1rem;
            font-size: 1rem;
        }}
        .footer-col ul {{ list-style: none; }}
        .footer-col li {{ margin-bottom: 0.5rem; }}
        .footer-col a {{ color: var(--text-secondary); text-decoration: none; }}
        .footer-col a:hover {{ color: var(--accent-leather); }}
        @media (max-width: 768px) {{
            h1 {{ font-size: 1.75rem; }}
            .hero-section {{ padding: 1.5rem; }}
            .section-card {{ padding: 1.5rem; }}
            .cta-primary {{ width: 100%; text-align: center; }}
            .btn-colab {{ width: 100%; justify-content: center; }}
        }}
    </style>
</head>
<body>

    <!-- Header Navigation -->
    <header>
        <div class="header-inner">
            <a href="index.html" class="brand-logo">BAGON<span>SA</span></a>
            <nav class="nav-links">
                <a href="index.html">Specification Hub</a>
                <a href="{silo_url}" target="_blank" rel="noopener">Official Store</a>
                <a href="{config.STORE_URL}" target="_blank" rel="noopener">BAGONSA Brand</a>
            </nav>
        </div>
    </header>

    <div class="container">
        <!-- Breadcrumbs -->
        <div class="breadcrumbs">
            <a href="index.html">Home Directory</a> &gt; 
            <a href="{silo_url}" target="_blank" rel="noopener">{silo_name}</a> &gt; 
            <span>{kw}</span>
        </div>

        <!-- Hero Section -->
        <section class="hero-section">
            <span class="badge-silo">{silo_info.get('icon', '👜')} {silo_info.get('short_name', 'Leather')}</span>
            <span class="badge-mod">★ {buyer_mod}</span>
            <h1>{kw}</h1>
            
            <div class="hero-meta">
                <span class="price">{price_range}</span>
                <span class="rating">{"★" * 5} <strong>{rating_val} / 5.0</strong> ({review_cnt} Verified Reviews)</span>
                <span>⚡ Express 3–5 Day DHL Worldwide Shipping</span>
            </div>

            <p class="hero-hook">{content['hero_hook']}</p>
            <p class="hero-narrative">{content['hero_narrative']}</p>

            <div class="cta-box">
                <a href="{target_url}" class="cta-primary" target="_blank" rel="noopener">
                    Explore Handcrafted Collection at BAGONSA Store &rarr;
                </a>
                <a href="{colab_url}" class="btn-colab" target="_blank" rel="noopener">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
                    Open Google Colab Spec Sheet
                </a>
            </div>
        </section>

        <!-- Technical Specifications Table -->
        <section class="section-card">
            <h2>Artisanal Engineering & Technical Specifications</h2>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">
                Every component of the BAGONSA {kw} is built to rigorous architectural tolerances:
            </p>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Specification</th>
                            <th>Artisanal Build Standard</th>
                            <th>Functional Benefit</th>
                        </tr>
                    </thead>
                    <tbody>
                        {specs_rows_html}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Full-Grain vs Commercial Leather Comparison -->
        <section class="section-card">
            <h2>{comp_table['title']}</h2>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">
                {comp_table['description']}
            </p>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>BAGONSA Handcrafted Full-Grain</th>
                            <th>Commercial Split Leather</th>
                            <th>Faux / Synthetic Leather</th>
                        </tr>
                    </thead>
                    <tbody>
                        {comp_rows_html}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Leather Care Guide -->
        <section class="section-card">
            <h2>{care_guide['title']}</h2>
            <p style="color: var(--text-secondary); margin-bottom: 0.5rem;">
                <strong>Care Protocol:</strong> {care_guide['philosophy']} (Recommended frequency: <em>{care_guide['frequency']}</em>).
            </p>
            <ol class="care-list">
                {care_steps_html}
            </ol>
        </section>

        <!-- Customer Reviews -->
        <section class="section-card">
            <h2>Verified Buyer Experiences & Feedback</h2>
            <div class="reviews-grid">
                {reviews_html}
            </div>
        </section>

        <!-- Dynamic Frequently Asked Questions -->
        <section class="section-card">
            <h2>Frequently Asked Buyer Questions</h2>
            <div class="faq-list">
                {faqs_html}
            </div>
        </section>

        <!-- Direct Workshop CTA Banner -->
        <div class="banner-direct">
            <h3>Handcrafted by BAGONSA Artisans</h3>
            <p>
                Experience 100% full-grain leather goods backed by solid brass hardware, YKK zippers, 
                and guaranteed Express 3–5 Business Day DHL delivery to USA, Canada, UK, and EU.
            </p>
            <a href="{target_url}" class="cta-primary" target="_blank" rel="noopener">
                Order {kw} Directly at BAGONSA Workshop &rarr;
            </a>
        </div>

        <!-- Google Colab Cross-Link Box -->
        <div class="section-card" style="border-left: 4px solid var(--accent-brass);">
            <h3 style="margin-bottom: 0.5rem; color: var(--text-primary);">Interactive Colab Specification Document</h3>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">
                View the cloud-executable Jupyter/Colab version of this technical review on Google Colaboratory. 
                Googlebot and data analysts can cross-reference complete material integrity specs and benchmark analyses:
            </p>
            <a href="{colab_url}" class="btn-colab" target="_blank" rel="noopener">
                Launch Google Colab Notebook ({slug}.ipynb) &rarr;
            </a>
        </div>

        <!-- Internal Silo & Cross-Silo Crawl Loop -->
        <section class="section-card">
            <h2>Related Artisanal Leather Buyer Guides</h2>
            <div class="links-grid">
                <div class="links-column">
                    <h3 style="font-size: 1.1rem; color: var(--accent-leather); margin-bottom: 1rem;">
                        More in {silo_name}
                    </h3>
                    <ul>
                        {same_silo_html}
                    </ul>
                </div>
                <div class="links-column">
                    <h3 style="font-size: 1.1rem; color: var(--text-secondary); margin-bottom: 1rem;">
                        Cross-Category Recommendations
                    </h3>
                    <ul>
                        {cross_silo_html}
                    </ul>
                </div>
            </div>
        </section>
    </div>

    <!-- Global Footer -->
    <footer>
        <div class="footer-inner">
            <div class="footer-col" style="max-width: 320px;">
                <h4 style="letter-spacing: 0.1em; text-transform: uppercase;">BAGONSA Leather Goods</h4>
                <p>Authentic full-grain & top-grain handcrafted leather goods. Hand-assembled with solid brass hardware, YKK zippers, and DHL express courier fulfillment.</p>
                <p style="margin-top: 0.75rem;"><strong>Support:</strong> {config.SUPPORT_EMAIL}</p>
            </div>
            <div class="footer-col">
                <h4>Product Categories</h4>
                <ul>
                    <li><a href="https://bagonsales.shop/collections/leather-backpacks" target="_blank" rel="noopener">Leather Backpacks</a></li>
                    <li><a href="https://bagonsales.shop/collections/leather-jackets" target="_blank" rel="noopener">Vintage Leather Jackets</a></li>
                    <li><a href="https://bagonsales.shop/collections/leather-handbags" target="_blank" rel="noopener">Croco Handbags & Totes</a></li>
                    <li><a href="https://bagonsales.shop/collections/leather-travel-bags" target="_blank" rel="noopener">Travel Duffels & Briefcases</a></li>
                    <li><a href="https://bagonsales.shop/collections/leather-footwear" target="_blank" rel="noopener">Artisanal Boots & Footwear</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>System & Index Hub</h4>
                <ul>
                    <li><a href="index.html">Specification Index (100 Guides)</a></li>
                    <li><a href="sitemap.xml">XML Sitemap</a></li>
                    <li><a href="robots.txt">Robots Directive</a></li>
                    <li><a href="{config.STORE_URL}" target="_blank" rel="noopener">Official BAGONSA Store</a></li>
                </ul>
            </div>
        </div>
        <div style="text-align: center; margin-top: 2rem; border-top: 1px solid var(--border-light); padding-top: 1.5rem; font-size: 0.85rem;">
            &copy; 2026 {config.BRAND_NAME}. All rights reserved. 100% Authentic Full-Grain Leather Goods.
        </div>
    </footer>

</body>
</html>
"""
    return html_content


def render_hub_index(keywords: List[Dict[str, Any]]) -> str:
    """Compiles the central index.html directory hub displaying all 100 guides categorized by Silo."""
    silos_grouped: Dict[str, List[Dict[str, Any]]] = {}
    for kw in keywords:
        s = kw["silo_category"]
        if s not in silos_grouped:
            silos_grouped[s] = []
        silos_grouped[s].append(kw)

    sections_html = ""
    for silo_key, items in silos_grouped.items():
        silo_info = config.SILO_CATEGORIES.get(silo_key, {})
        silo_title = silo_info.get("name", silo_key)
        silo_icon = silo_info.get("icon", "👜")
        silo_desc = silo_info.get("description", "")
        silo_url = silo_info.get("target_url", config.STORE_URL)

        cards_html = "".join([
            f"""<div class="hub-card">
                <span class="hub-card-mod">{item['buyer_modifier']}</span>
                <h3><a href="{item['slug']}.html">{item['keyword']}</a></h3>
                <div class="hub-card-meta">
                    <span class="hub-price">{item['price_range']}</span>
                    <span class="hub-rating">★ {item['rating_value']} ({item['review_count']} reviews)</span>
                </div>
                <div class="hub-card-links">
                    <a href="{item['slug']}.html" class="hub-btn-read">Read Specification &rarr;</a>
                    <a href="{item['target_store_url']}" class="hub-btn-store" target="_blank" rel="noopener">Shop Store</a>
                </div>
            </div>"""
            for item in items
        ])

        sections_html += f"""
        <section class="hub-silo-section" id="{silo_key}">
            <div class="hub-silo-header">
                <div>
                    <h2>{silo_icon} {silo_title}</h2>
                    <p>{silo_desc}</p>
                </div>
                <a href="{silo_url}" class="hub-silo-shop-btn" target="_blank" rel="noopener">
                    Shop Collection &rarr;
                </a>
            </div>
            <div class="hub-cards-grid">
                {cards_html}
            </div>
        </section>
        """

    canonical_index = f"{config.GITHUB_PAGES_BASE_URL}index.html"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BAGONSA Full-Grain Leather Specification Directory & Master Guide</title>
    <meta name="description" content="Explore BAGONSA's complete technical specification directory for 100 handcrafted full-grain leather backpacks, vintage jackets, croco handbags, travel duffels, and boots.">
    <link rel="canonical" href="{canonical_index}">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    <meta name="google-site-verification" content="google9d2790f8d29dbd34.html">
    <meta name="google-site-verification" content="google9d2790f8d29dbd34">
    <meta name="google-site-verification" content="2plITmBLaHMbWEm8O0qjfrzMyH0yhIDoCL-5Exq1vmU">
    
    <style>
        :root {{
            --bg-canvas: #faf8f5;
            --bg-card: #ffffff;
            --text-primary: #1c1917;
            --text-secondary: #57534e;
            --text-muted: #78716c;
            --accent-leather: #8b4513;
            --accent-brass: #b45309;
            --border-light: #e7e5e4;
            --font-stack: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Georgia, serif;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-canvas);
            color: var(--text-primary);
            font-family: var(--font-stack);
            line-height: 1.6;
        }}
        header {{
            background: #ffffff;
            border-bottom: 1px solid var(--border-light);
            padding: 1.25rem 0;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .header-inner {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .brand-logo {{
            font-size: 1.4rem;
            font-weight: 800;
            letter-spacing: 0.15em;
            color: var(--text-primary);
            text-decoration: none;
            text-transform: uppercase;
        }}
        .brand-logo span {{ color: var(--accent-leather); }}
        .nav-links a {{
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.95rem;
            font-weight: 600;
            margin-left: 1.5rem;
        }}
        .nav-links a:hover {{ color: var(--accent-leather); }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2.5rem 1.5rem 5rem;
        }}
        .hub-hero {{
            background: linear-gradient(135deg, #1c1917 0%, #292524 100%);
            color: #ffffff;
            border-radius: 16px;
            padding: 3.5rem 2.5rem;
            text-align: center;
            margin-bottom: 3.5rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .hub-hero h1 {{
            font-size: 2.75rem;
            margin-bottom: 1rem;
            color: #ffffff;
            font-weight: 800;
        }}
        .hub-hero p {{
            font-size: 1.2rem;
            color: #d6d3d1;
            max-width: 780px;
            margin: 0 auto 2rem;
        }}
        .hub-pills {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 0.75rem;
        }}
        .hub-pills a {{
            background: rgba(255,255,255,0.12);
            color: #ffffff;
            text-decoration: none;
            padding: 0.6rem 1.2rem;
            border-radius: 9999px;
            font-size: 0.9rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        .hub-pills a:hover {{
            background: var(--accent-brass);
        }}
        .hub-silo-section {{
            margin-bottom: 4rem;
        }}
        .hub-silo-header {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: flex-end;
            margin-bottom: 1.75rem;
            border-bottom: 2px solid var(--border-light);
            padding-bottom: 1rem;
            gap: 1rem;
        }}
        .hub-silo-header h2 {{
            font-size: 1.75rem;
            color: var(--text-primary);
        }}
        .hub-silo-header p {{
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin-top: 0.25rem;
        }}
        .hub-silo-shop-btn {{
            color: var(--accent-leather);
            font-weight: 700;
            text-decoration: none;
            font-size: 0.95rem;
        }}
        .hub-silo-shop-btn:hover {{ text-decoration: underline; }}
        .hub-cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
            gap: 1.5rem;
        }}
        .hub-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-light);
            border-radius: 10px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .hub-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.06);
            border-color: #cbd5e1;
        }}
        .hub-card-mod {{
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            color: #0369a1;
            background: #e0f2fe;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            display: inline-block;
            margin-bottom: 0.75rem;
            align-self: flex-start;
        }}
        .hub-card h3 {{
            font-size: 1.05rem;
            line-height: 1.35;
            margin-bottom: 0.75rem;
        }}
        .hub-card h3 a {{
            color: var(--text-primary);
            text-decoration: none;
        }}
        .hub-card h3 a:hover {{
            color: var(--accent-leather);
        }}
        .hub-card-meta {{
            display: flex;
            justify-content: space-between;
            font-size: 0.85rem;
            margin-bottom: 1.25rem;
            border-top: 1px solid #f1f5f9;
            padding-top: 0.75rem;
        }}
        .hub-price {{ font-weight: 700; color: var(--accent-leather); }}
        .hub-rating {{ color: #d97706; }}
        .hub-card-links {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
        }}
        .hub-btn-read {{
            color: var(--text-primary);
            font-weight: 600;
            text-decoration: none;
        }}
        .hub-btn-read:hover {{ color: var(--accent-leather); text-decoration: underline; }}
        .hub-btn-store {{
            color: var(--accent-brass);
            text-decoration: none;
            font-weight: 700;
        }}
        footer {{
            background: #ffffff;
            border-top: 1px solid var(--border-light);
            padding: 3rem 0;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>

    <header>
        <div class="header-inner">
            <a href="index.html" class="brand-logo">BAGON<span>SA</span></a>
            <nav class="nav-links">
                <a href="#leather-backpacks">Backpacks</a>
                <a href="#leather-jackets">Jackets</a>
                <a href="#handbags-totes">Handbags</a>
                <a href="#travel-duffels">Travel Duffels</a>
                <a href="#leather-footwear">Footwear</a>
                <a href="colab-directory.html" style="color: var(--accent-brass); font-weight: 700;">Colab Directory (100)</a>
                <a href="{config.STORE_URL}" target="_blank" rel="noopener">Official Store</a>
            </nav>
        </div>
    </header>

    <div class="container">
        <div class="hub-hero">
            <h1>BAGONSA Artisanal Leather Specification Directory</h1>
            <p>
                Comprehensive material integrity analysis, technical blueprints, and verified buyer specifications 
                for 100 handcrafted full-grain leather goods. Hand-assembled with solid brass hardware, YKK zippers, 
                and Express 3-5 day DHL delivery worldwide.
            </p>
            <div class="hub-pills">
                <a href="#leather-backpacks">🎒 20 Leather Backpack Guides</a>
                <a href="#leather-jackets">🧥 20 Vintage Jacket Guides</a>
                <a href="#handbags-totes">👜 20 Handbag & Tote Guides</a>
                <a href="#travel-duffels">🧳 20 Travel Duffel Guides</a>
                <a href="#leather-footwear">👞 20 Artisanal Boot Guides</a>
            </div>
        </div>

        {sections_html}
    </div>

    <footer>
        <p>&copy; 2026 {config.BRAND_NAME}. Handcrafted Full-Grain & Top-Grain Leather Goods.</p>
        <p style="margin-top: 0.5rem;">
            <a href="sitemap.xml" style="color: var(--accent-leather); text-decoration: none;">XML Sitemap</a> | 
            <a href="robots.txt" style="color: var(--accent-leather); text-decoration: none;">Robots.txt</a> | 
            <a href="{config.STORE_URL}" style="color: var(--accent-leather); text-decoration: none;">Visit BAGONSA Store</a>
        </p>
    </footer>

</body>
</html>
"""


def render_colab_directory(keywords: List[Dict[str, Any]]) -> str:
    """Builds an HTML directory linking all 100 Google Colab parasite notebooks."""
    silos_grouped: Dict[str, List[Dict[str, Any]]] = {}
    for kw in keywords:
        s = kw["silo_category"]
        if s not in silos_grouped:
            silos_grouped[s] = []
        silos_grouped[s].append(kw)

    sections_html = ""
    for silo_key, items in silos_grouped.items():
        silo_info = config.SILO_CATEGORIES.get(silo_key, {})
        silo_title = silo_info.get("name", silo_key)
        silo_icon = silo_info.get("icon", "👜")
        silo_url = silo_info.get("target_url", config.STORE_URL)

        cards_html = "".join([
            f"""<div class="colab-card">
                <span class="badge-colab">Google Colab .ipynb</span>
                <h3>{item['keyword']}</h3>
                <p class="colab-price">{item['price_range']} · ★ {item['rating_value']} ({item['review_count']} reviews)</p>
                <div class="colab-links">
                    <a href="{config.COLAB_BASE_URL}{item['slug']}.ipynb" target="_blank" rel="noopener" class="btn-colab-direct">
                        Open on Google Colab &rarr;
                    </a>
                    <a href="{item['slug']}.html" class="btn-web-direct">Web Guide</a>
                </div>
            </div>"""
            for item in items
        ])

        sections_html += f"""
        <section class="colab-silo-section" id="{silo_key}">
            <div class="colab-silo-header">
                <h2>{silo_icon} {silo_title} ({len(items)} Colab Notebooks)</h2>
                <a href="{silo_url}" target="_blank" rel="noopener" class="store-link">Shop Category &rarr;</a>
            </div>
            <div class="colab-cards-grid">
                {cards_html}
            </div>
        </section>
        """

    canonical_colab = f"{config.GITHUB_PAGES_BASE_URL}colab-directory.html"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BAGONSA Google Colab Technical Specifications Directory (100 Notebooks)</title>
    <meta name="description" content="Access 100 cloud-rendered Google Colab technical notebooks on colab.research.google.com for BAGONSA handcrafted full-grain leather goods.">
    <link rel="canonical" href="{canonical_colab}">
    <meta name="robots" content="index, follow">
    <style>
        :root {{
            --bg-canvas: #faf8f5;
            --bg-card: #ffffff;
            --text-primary: #1c1917;
            --text-secondary: #57534e;
            --accent-leather: #8b4513;
            --accent-brass: #b45309;
            --border-light: #e7e5e4;
            --font-stack: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Georgia, serif;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ background-color: var(--bg-canvas); color: var(--text-primary); font-family: var(--font-stack); line-height: 1.6; }}
        header {{ background: #ffffff; border-bottom: 1px solid var(--border-light); padding: 1.25rem 0; position: sticky; top: 0; z-index: 100; }}
        .header-inner {{ max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; display: flex; align-items: center; justify-content: space-between; }}
        .brand-logo {{ font-size: 1.4rem; font-weight: 800; letter-spacing: 0.15em; color: var(--text-primary); text-decoration: none; text-transform: uppercase; }}
        .brand-logo span {{ color: var(--accent-leather); }}
        .nav-links a {{ color: var(--text-secondary); text-decoration: none; font-size: 0.95rem; font-weight: 600; margin-left: 1.5rem; }}
        .nav-links a:hover {{ color: var(--accent-leather); }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2.5rem 1.5rem 5rem; }}
        .hero {{ background: linear-gradient(135deg, #1c1917 0%, #292524 100%); color: #ffffff; border-radius: 16px; padding: 3rem 2rem; text-align: center; margin-bottom: 3rem; }}
        .hero h1 {{ font-size: 2.5rem; margin-bottom: 1rem; color: #ffffff; }}
        .hero p {{ font-size: 1.15rem; color: #d6d3d1; max-width: 750px; margin: 0 auto 1.5rem; }}
        .colab-silo-section {{ margin-bottom: 3.5rem; }}
        .colab-silo-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; border-bottom: 2px solid var(--border-light); padding-bottom: 0.75rem; }}
        .colab-silo-header h2 {{ font-size: 1.5rem; color: var(--text-primary); }}
        .store-link {{ color: var(--accent-leather); text-decoration: none; font-weight: 700; }}
        .colab-cards-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem; }}
        .colab-card {{ background: var(--bg-card); border: 1px solid var(--border-light); border-radius: 10px; padding: 1.25rem; display: flex; flex-direction: column; justify-content: space-between; }}
        .colab-card:hover {{ border-color: var(--accent-brass); box-shadow: 0 4px 16px rgba(0,0,0,0.06); }}
        .badge-colab {{ font-size: 0.75rem; font-weight: 700; color: #b45309; background: #fef3c7; padding: 0.2rem 0.5rem; border-radius: 4px; display: inline-block; margin-bottom: 0.5rem; align-self: flex-start; }}
        .colab-card h3 {{ font-size: 1rem; margin-bottom: 0.5rem; }}
        .colab-price {{ font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1rem; }}
        .colab-links {{ display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; }}
        .btn-colab-direct {{ color: #ffffff; background: #b45309; text-decoration: none; font-weight: 700; padding: 0.4rem 0.8rem; border-radius: 6px; }}
        .btn-colab-direct:hover {{ background: #92400e; }}
        .btn-web-direct {{ color: var(--text-secondary); text-decoration: none; font-weight: 600; }}
        .btn-web-direct:hover {{ color: var(--accent-leather); }}
        footer {{ background: #ffffff; border-top: 1px solid var(--border-light); padding: 2.5rem 0; text-align: center; color: var(--text-secondary); font-size: 0.9rem; }}
    </style>
</head>
<body>
    <header>
        <div class="header-inner">
            <a href="index.html" class="brand-logo">BAGON<span>SA</span></a>
            <nav class="nav-links">
                <a href="index.html">Master Directory Hub</a>
                <a href="colab-directory.html" style="color: var(--accent-brass);">Colab Directory</a>
                <a href="{config.STORE_URL}" target="_blank" rel="noopener">Official Store</a>
            </nav>
        </div>
    </header>
    <div class="container">
        <div class="hero">
            <h1>BAGONSA Google Colab Notebooks Directory</h1>
            <p>100 open cloud-executable specification documents hosted on Google Research Colab (colab.research.google.com). Every notebook provides verified material blueprints, benchmark matrices, and direct workshop ordering.</p>
        </div>
        {sections_html}
    </div>
    <footer>
        <p>&copy; 2026 {config.BRAND_NAME}. Handcrafted Full-Grain & Top-Grain Leather Goods.</p>
        <p style="margin-top: 0.5rem;"><a href="index.html">HTML Specification Hub</a> | <a href="sitemap.xml">XML Sitemap</a> | <a href="{config.STORE_URL}">BAGONSA Official Store</a></p>
    </footer>
</body>
</html>
"""


def render_sitemap_xml(keywords: List[Dict[str, Any]]) -> str:
    """Builds a compliant XML sitemap listing index.html, colab-directory.html, and all 100 pages."""
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    base_url = config.GITHUB_PAGES_BASE_URL

    urls_xml = [
        f"""  <url>
    <loc>{base_url}index.html</loc>
    <lastmod>{now_iso}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""",
        f"""  <url>
    <loc>{base_url}colab-directory.html</loc>
    <lastmod>{now_iso}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>"""
    ]

    for item in keywords:
        page_url = f"{base_url}{item['slug']}.html"
        urls_xml.append(
            f"""  <url>
    <loc>{page_url}</loc>
    <lastmod>{now_iso}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>"""
        )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls_xml)}
</urlset>
"""


def render_robots_txt() -> str:
    """Builds compliant robots.txt with sitemap directive."""
    sitemap_url = f"{config.GITHUB_PAGES_BASE_URL}sitemap.xml"
    return f"""User-agent: *
Allow: /

Sitemap: {sitemap_url}
"""


def main():
    """Main build process for static HTML pages, index hub, sitemap, and robots.txt."""
    print("=" * 65)
    print("BAGONSA STATIC HTML & SEO SCHEMA COMPILER")
    print("=" * 65)

    keywords = load_keywords()
    print(f"Loaded {len(keywords)} keywords from {config.KEYWORDS_CSV}")

    # Ensure output directory exists
    config.DIST_PAGES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Generate 100 individual HTML pages
    for i, item in enumerate(keywords, start=1):
        content = get_page_content(item)
        internal_links = get_internal_links(item, keywords)
        html_output = render_html_page(item, content, internal_links)

        page_file = config.DIST_PAGES_DIR / f"{item['slug']}.html"
        with open(page_file, "w", encoding="utf-8") as f:
            f.write(html_output)

        if i % 25 == 0 or i == len(keywords):
            print(f"  [OK] Generated {i}/{len(keywords)} pages: {page_file.name}")

    # 2. Generate index.html directory hub
    index_html = render_hub_index(keywords)
    index_file = config.DIST_PAGES_DIR / "index.html"
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"  [OK] Generated Hub Index: {index_file.name}")

    # 3. Generate colab-directory.html
    colab_dir_html = render_colab_directory(keywords)
    colab_dir_file = config.DIST_PAGES_DIR / "colab-directory.html"
    with open(colab_dir_file, "w", encoding="utf-8") as f:
        f.write(colab_dir_html)
    print(f"  [OK] Generated Colab Directory: {colab_dir_file.name}")

    # 4. Generate sitemap.xml
    sitemap_xml = render_sitemap_xml(keywords)
    sitemap_file = config.DIST_PAGES_DIR / "sitemap.xml"
    with open(sitemap_file, "w", encoding="utf-8") as f:
        f.write(sitemap_xml)
    print(f"  [OK] Generated Sitemap: {sitemap_file.name}")

    # 4. Generate robots.txt
    robots_txt = render_robots_txt()
    robots_file = config.DIST_PAGES_DIR / "robots.txt"
    with open(robots_file, "w", encoding="utf-8") as f:
        f.write(robots_txt)
    print(f"  [OK] Generated Robots: {robots_file.name}")

    print("=" * 65)
    print(f"SUCCESS: Compiled 100 HTML pages + index.html + sitemap.xml + robots.txt into {config.DIST_PAGES_DIR}")
    print("=" * 65)


if __name__ == "__main__":
    main()
