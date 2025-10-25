# cardivore_ai/utils/widgets.py
import ipywidgets as widgets
from IPython.display import display, clear_output

def file_selector(label="Select a CSV file"):
    """File picker widget for uploading or browsing a local CSV."""
    uploader = widgets.FileUpload(
        accept='.csv',
        multiple=False,
        description=label,
        button_style='info'
    )
    display(uploader)
    return uploader

def dropdown_from_list(options, label="Select an option"):
    """Reusable dropdown widget."""
    dropdown = widgets.Dropdown(
        options=options,
        description=label,
        style={'description_width': 'initial'},
        layout=widgets.Layout(width="400px")
    )
    display(dropdown)
    return dropdown

def build_mapping_ui(csv_headers, db_headers):
    """
    Create a row of dropdowns to map each CSV header to a DB header or 'DROP'.
    Returns a dict of widgets keyed by CSV header.
    """
    mapping_widgets = {}
    mapping_options = db_headers + ["DROP"]

    items = []
    for col in csv_headers:
        label = widgets.Label(value=col)
        dropdown = widgets.Dropdown(
            options=mapping_options,
            description="",
            layout=widgets.Layout(width="250px")
        )
        mapping_widgets[col] = dropdown
        items.append(widgets.HBox([label, dropdown]))
    mapping_box = widgets.VBox(items)
    display(mapping_box)
    return mapping_widgets

def action_buttons():
    """Generate Import and Save buttons."""
    btn_import = widgets.Button(description="Import Data", button_style='success', icon='upload')
    btn_save = widgets.Button(description="Save Mapping", button_style='warning', icon='save')
    display(widgets.HBox([btn_import, btn_save]))
    return btn_import, btn_save

def show_message(message, color="green"):
    """Quick rich-style message display."""
    out = widgets.Output()
    with out:
        clear_output()
        print(f"[{color.upper()}] {message}")
    display(out)
