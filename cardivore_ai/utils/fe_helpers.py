# Placeholder for frontend (UI/Jupyter) helpers.
# Example: display Rich tables, Jupyter widgets, etc.

def print_section(title: str):
    """Simple formatting helper for console/Jupyter output."""
    print(f"\n{'=' * 50}\n{title.upper()}\n{'=' * 50}")

# cardivore_ai/utils/fe_helpers.py
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, HTML

def display_roi_filter(summary_df: pd.DataFrame):
    """
    Interactive ROI + Max Raw filters with clickable eBay links.

    Requires columns:
      ['search_string', 'ebay_url', 'roi_multiple', 'raw_avg', 'psa10_avg']
    """
    # --- Sliders ---
    roi_slider = widgets.FloatSlider(
        value=3.5, min=1.0, max=10.0, step=0.5,
        description="ROI Target ×", readout_format=".1f", continuous_update=False
    )
    raw_slider = widgets.FloatSlider(
        value=50.0, min=5.0, max=500.0, step=5.0,
        description="Max Raw ($)", readout_format=".0f", continuous_update=False
    )

    # --- Renderer function (no return; uses display()) ---
    def show_filtered(target_roi=3.5, max_raw=50.0):
        df = summary_df[
            (summary_df["roi_multiple"] >= target_roi) &
            (summary_df["raw_avg"] <= max_raw)
        ].copy()

        df = df.sort_values("roi_multiple", ascending=False)

        # Format columns
        df["Raw Avg ($)"] = df["raw_avg"].map("${:,.2f}".format)
        df["PSA10 Avg ($)"] = df["psa10_avg"].map("${:,.2f}".format)
        df["ROI ×"] = df["roi_multiple"].map("{:.2f}".format)
        df["eBay Link"] = df["ebay_url"].apply(lambda u: f'<a href="{u}" target="_blank">🔗 View</a>')

        cols = ["search_string", "Raw Avg ($)", "PSA10 Avg ($)", "ROI ×", "eBay Link"]
        html_table = df[cols].to_html(escape=False, index=False)

        styled_html = f"""
        <style>
            table {{ font-family: Arial, sans-serif; border-collapse: collapse; width: 100%; }}
            th {{ background:#2b2b2b; color:#fff; padding:6px; text-align:left; }}
            td {{ padding:6px; border-bottom:1px solid #ddd; }}
            tr:hover {{ background:#33333330; }}
        </style>
        {html_table}
        """
        display(HTML(styled_html))

    # --- Wire sliders to output correctly ---
    out = widgets.interactive_output(show_filtered, {"target_roi": roi_slider, "max_raw": raw_slider})

    # Display the controls + the bound output
    display(widgets.VBox([widgets.HBox([roi_slider, raw_slider]), out]))

    # Initial render (optional; interactive_output will render once too)
    # show_filtered(roi_slider.value, raw_slider.value)
