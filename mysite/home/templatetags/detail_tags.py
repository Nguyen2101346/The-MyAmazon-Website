from django import template
register = template.Library()

@register.filter
def render_details(details):
    important_keys = [
        "Dimensions", "Item Weight", "Item model number", "Brand", "Manufacturer",
        "Size", "Color", "Wattage", "Capacity", "Voltage", "Sun Protection Factor"
    ]
    html = ""
    for key in important_keys:
        value = details.get(key)
        if value:
            html += f"<tr><th>{key}</th><td>{value}</td></tr>\n"
    return html
