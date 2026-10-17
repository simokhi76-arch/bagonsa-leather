# BAGONSA Programmatic & Parasite SEO Automation Engine

A high-performance, production-ready Programmatic SEO & Multi-Platform Parasite Engine architected for **BAGONSA** ([https://bagonsales.shop/](https://bagonsales.shop/)) — makers of 100% authentic handcrafted full-grain and top-grain leather goods.

---

## 1. System Architecture

```text
bagonsa-seo-engine/
├── config.py                      # Central configuration (URLs, GitHub endpoints, GCS bucket, deep links)
├── data/
│   └── keywords_100.csv           # 100 buyer-intent long-tail keywords across 5 product silos
├── src/
│   ├── content_matrix.py          # Modular text engine, deterministic spinning, comparison tables, dynamic FAQs
│   ├── build_html_pages.py        # Compiles 100 HTML5 pages + index.html + sitemap.xml + robots.txt
│   ├── build_colab_notebooks.py   # Compiles 100 SEO-optimized .ipynb files for colab.research.google.com
│   └── google_indexer.py          # Pushes sitemap URLs to Google Indexing API via Service Account
├── dist_pages/                    # Compiled static HTML5 site (100 guides + index.html + sitemap.xml + robots.txt)
├── dist_colab/                    # Compiled .ipynb Jupyter/Colab notebooks for Google Colab parasite indexing
├── deploy_github_safe.sh          # Single-commit Git push script (POSIX bash)
├── deploy_github_safe.ps1         # Single-commit Git push script (PowerShell)
├── deploy_gcs_bucket.py           # Static site uploader for Google Cloud Storage (storage.googleapis.com)
├── .github/
│   └── workflows/
│       └── drip_publish.yml       # GitHub Actions CI/CD workflow for automated build & GitHub Pages deployment
└── requirements.txt               # Production Python dependencies
```

---

## 2. Product Silo Mapping (100 Keywords)

The engine maps 100 long-tail buyer-intent queries across 5 distinct product silos:

| Silo Category | Focus Products | Target Store URL |
| :--- | :--- | :--- |
| **Silo 1: Leather Backpacks & Laptop Bags** | 14-16" Laptop rucksacks, roll-tops, commuter packs | `https://bagonsales.shop/collections/leather-backpacks` |
| **Silo 2: Leather Jackets** | Vintage bombers, cafe racers, biker jackets, A-2 flight coats | `https://bagonsales.shop/collections/leather-jackets` |
| **Silo 3: Handbags & Totes** | Croco-embossed handbags, suede shoppers, crossbody satchels | `https://bagonsales.shop/collections/leather-handbags` |
| **Silo 4: Travel Duffels & Briefcases** | 45L/55L TSA carry-ons, shoe compartments, executive attache cases | `https://bagonsales.shop/collections/leather-travel-bags` |
| **Silo 5: Leather Boots & Footwear** | Goodyear-welted dress boots, Vibram commando lugs, loafers | `https://bagonsales.shop/collections/leather-footwear` |

---

## 3. Anti-Spam & Semantic SEO Architecture

1. **Deterministic MD5 Content Spinning (`src/content_matrix.py`):**
   - Derived using `hashlib.md5(keyword.encode())` to ensure reproducible yet non-repetitive page outputs.
   - Distinctive narrative intros, category-specific specs (e.g. laptop sleeve neoprene padding vs. jacket quilted linings and bi-swing action backs).
   - Full-Grain vs Commercial Leather comparison tables and actionable leather care protocols.
   - 4 Dynamic FAQs per guide tailored to the exact keyword, shipping region (USA, Canada, UK, EU, or Global), pricing tier, and returns.

2. **Dual JSON-LD Schema Injection (`src/build_html_pages.py`):**
   - `Product` Schema: Valid offer, aggregate rating (4.8 - 5.0), verified customer reviews, SKU, and direct store URL.
   - `FAQPage` Schema: Semantic Q&A pairs recognized by Google Rich Results.

3. **Closed-Loop Crawl Architecture:**
   - Every page links to `index.html` (hub).
   - Horizontally links to **5 related guides in the same silo**.
   - Horizontally links to **2 cross-silo guides**.
   - Cross-links to the corresponding **Google Colab notebook** to accelerate parasite indexing.

4. **Zero-Redirect Compliance:**
   - No `<meta http-equiv="refresh">` or JavaScript location redirects.
   - Prominent, natural HTML Call-To-Action buttons (`class="cta-primary"`) driving high-intent traffic directly to `https://bagonsales.shop/`.

---

## 4. Google Colab Parasite Engine (`src/build_colab_notebooks.py`)

Every generated `.ipynb` file in `dist_colab/`:
- Contains **pure Markdown cells** (no executable Python cells) to avoid abuse flags.
- Renders natively on Google's high-authority domain:
  `https://colab.research.google.com/github/{GITHUB_USER}/{REPO_NAME}/blob/main/dist_colab/{slug}.ipynb`
- Features Open-in-Colab badges, Markdown specification tables, material benchmarks, and canonical links pointing back to both the GitHub Pages guide and `https://bagonsales.shop/`.

---

## 5. Quickstart & Execution Guide

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Compile Static HTML Pages & Sitemap
```bash
python src/build_html_pages.py
```
Outputs 100 HTML pages, `index.html`, `sitemap.xml`, and `robots.txt` into `dist_pages/`.

### Step 3: Compile Google Colab Parasite Notebooks
```bash
python src/build_colab_notebooks.py
```
Outputs 100 `.ipynb` files into `dist_colab/`.

### Step 4: Safe Single-Commit Deployment
Avoids GitHub API secondary rate limits by bundling everything into a single atomic commit:

**Using Bash (Linux / macOS / Git Bash):**
```bash
export GITHUB_TOKEN="ghp_your_personal_access_token"
./deploy_github_safe.sh
```

**Using PowerShell (Windows):**
```powershell
$env:GITHUB_TOKEN = "ghp_your_personal_access_token"
.\deploy_github_safe.ps1
```

### Step 5: Google Indexing API Submission
Test submissions in dry-run mode:
```bash
python src/google_indexer.py --dry-run --limit 10
```
Run live submissions with your Google Cloud Service Account key:
```bash
python src/google_indexer.py --key-file service_account.json --delay 1.0
```

### Step 6: Google Cloud Storage Deployment (Optional)
Test upload in dry-run mode:
```bash
python deploy_gcs_bucket.py --dry-run
```
Execute live bucket synchronization:
```bash
python deploy_gcs_bucket.py --bucket your-gcs-bucket-name
```
