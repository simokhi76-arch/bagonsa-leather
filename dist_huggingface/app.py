import gradio as gr
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
