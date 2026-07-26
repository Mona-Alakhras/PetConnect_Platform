"""
Inline SVG icon system for PetConnect.
 
Renders crisp, self-hosted stroke icons with zero external requests.
Icons inherit their colour from the surrounding text (``currentColor``)
and their size from the ``--icon-size`` CSS custom property, so they can
be styled entirely from the stylesheets.
 
Usage in templates::
 
    {% load icons %}
    {% icon "paw" %}
    {% icon "map-pin" class="icon icon--muted" %}
    {% icon "check" size="1.25rem" %}
"""
 
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
 
register = template.Library()
 
 
# Icon geometry is drawn on a 24x24 grid with a 2px stroke.
# Paths are adapted from the Lucide icon set (ISC licensed).
ICONS = {
    # ---- Brand & animals ------------------------------------------------
    "paw": (
        '<circle cx="11" cy="4" r="2"/><circle cx="18" cy="8" r="2"/>'
        '<circle cx="20" cy="16" r="2"/>'
        '<path d="M9 10a5 5 0 0 1 5 5v3.5a3.5 3.5 0 0 1-6.84 1.045Q6.52 17.48 4.46 '
        '16.84A3.5 3.5 0 0 1 5.5 10Z"/>'
    ),
    "dog": (
        '<path d="M11.25 16.25h1.5L12 17z"/><path d="M16 14v.5"/><path d="M8 14v.5"/>'
        '<path d="M4.42 11.247A13.152 13.152 0 0 0 4 14.556C4 18.728 7.582 21 12 '
        '21s8-2.272 8-6.444a11.702 11.702 0 0 0-.493-3.309"/>'
        '<path d="M8.5 8.5c-.384 1.05-1.083 2.028-2.344 2.5-1.931.722-3.576-.297-3.656-1-.113-.994 '
        '1.177-6.53 4-7 1.923-.321 3.651.845 3.651 2.235A7.497 7.497 0 0 1 14 '
        '5.277c0-1.39 1.844-2.598 3.767-2.277 2.823.47 4.113 6.006 4 7-.08.703-1.725 '
        '1.722-3.656 1-1.261-.472-1.96-1.45-2.344-2.5"/>'
    ),
    "cat": (
        '<path d="M12 5c.67 0 1.35.09 2 .26 1.78-2 5.03-2.84 6.42-2.26 1.4.58-.42 7-.42 '
        '7 .57 1.07 1 2.24 1 3.44C21 17.9 16.97 21 12 21s-9-3-9-7.56c0-1.25.5-2.4 '
        '1-3.44 0 0-1.89-6.42-.5-7 1.39-.58 4.72.24 6.5 2.24A9.04 9.04 0 0 1 12 5Z"/>'
        '<path d="M8 14v.5"/><path d="M16 14v.5"/><path d="M11.25 16.25h1.5L12 17z"/>'
    ),
    "bird": (
        '<path d="M16 7h.01"/>'
        '<path d="M3.4 18H12a8 8 0 0 0 8-8V7a4 4 0 0 0-7.28-2.3L2 20"/>'
        '<path d="m20 7 2 .5-2 .5"/><path d="M10 18v3"/><path d="M14 17.75V21"/>'
        '<path d="M7 18a6 6 0 0 0 3.84-10.61"/>'
    ),
 
    # ---- Navigation -----------------------------------------------------
    "menu": '<path d="M4 12h16"/><path d="M4 6h16"/><path d="M4 18h16"/>',
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "arrow-right": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "arrow-left": '<path d="M19 12H5"/><path d="m12 19-7-7 7-7"/>',
    "chevron-left": '<path d="m15 18-6-6 6-6"/>',
    "chevron-right": '<path d="m9 18 6-6-6-6"/>',
    "external-link": (
        '<path d="M15 3h6v6"/><path d="M10 14 21 3"/>'
        '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>'
    ),
 
    # ---- Account --------------------------------------------------------
    "user": (
        '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>'
        '<circle cx="12" cy="7" r="4"/>'
    ),
    "users": (
        '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>'
        '<circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/>'
        '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
    ),
    "log-in": (
        '<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>'
        '<path d="m10 17 5-5-5-5"/><path d="M15 12H3"/>'
    ),
    "log-out": (
        '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>'
        '<path d="m16 17 5-5-5-5"/><path d="M21 12H9"/>'
    ),
    "shield-check": (
        '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 '
        '13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 '
        '17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>'
    ),
    "lock": (
        '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/>'
        '<path d="M7 11V7a5 5 0 0 1 10 0v4"/>'
    ),
 
    # ---- Content --------------------------------------------------------
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "calendar": (
        '<path d="M8 2v4"/><path d="M16 2v4"/>'
        '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>'
    ),
    "map-pin": (
        '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 '
        '20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>'
    ),
    "home": (
        '<path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/>'
        '<path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 '
        '0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
    ),
    "heart": (
        '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 '
        '2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>'
    ),
    "image": (
        '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>'
        '<circle cx="9" cy="9" r="2"/>'
        '<path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>'
    ),
    "upload": (
        '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
        '<path d="M17 8l-5-5-5 5"/><path d="M12 3v12"/>'
    ),
    "code": '<path d="m16 18 6-6-6-6"/><path d="m8 6-6 6 6 6"/>',
 
    # ---- Dashboard & workflow -------------------------------------------
    "layout-dashboard": (
        '<rect width="7" height="9" x="3" y="3" rx="1"/>'
        '<rect width="7" height="5" x="14" y="3" rx="1"/>'
        '<rect width="7" height="9" x="14" y="12" rx="1"/>'
        '<rect width="7" height="5" x="3" y="16" rx="1"/>'
    ),
    "clipboard-list": (
        '<rect width="8" height="4" x="8" y="2" rx="1" ry="1"/>'
        '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>'
        '<path d="M12 11h4"/><path d="M12 16h4"/><path d="M8 11h.01"/><path d="M8 16h.01"/>'
    ),
    "file-text": (
        '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/>'
        '<path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M16 13H8"/>'
        '<path d="M16 17H8"/><path d="M10 9H8"/>'
    ),
    "inbox": (
        '<path d="M22 12h-6l-2 3h-4l-2-3H2"/>'
        '<path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 '
        '0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>'
    ),
    "plus-circle": (
        '<circle cx="12" cy="12" r="10"/><path d="M8 12h8"/><path d="M12 8v8"/>'
    ),
    "trash": (
        '<path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>'
        '<path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>'
        '<path d="M10 11v6"/><path d="M14 11v6"/>'
    ),
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "check-circle": '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    "x-circle": (
        '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>'
    ),
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "alert-circle": (
        '<circle cx="12" cy="12" r="10"/><path d="M12 8v4"/><path d="M12 16h.01"/>'
    ),
    "info": (
        '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>'
    ),
    "mail": (
        '<rect width="20" height="16" x="2" y="4" rx="2"/>'
        '<path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>'
    ),
    "mail-check": (
        '<path d="M22 13V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v12c0 1.1.9 2 2 2h8"/>'
        '<path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>'
        '<path d="m16 19 2 2 4-4"/>'
    ),
    "send": (
        '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>'
    ),
 
    # ---- Social (filled marks) ------------------------------------------
    "facebook": (
        '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>'
    ),
    "instagram": (
        '<rect width="20" height="20" x="2" y="2" rx="5" ry="5"/>'
        '<path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>'
        '<path d="M17.5 6.5h.01"/>'
    ),
    "twitter-x": (
        '<path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 '
        '21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 '
        '4.126H5.117z"/>'
    ),
}
 
# Icons drawn as solid shapes rather than strokes.
FILLED = {"twitter-x"}
 
 
@register.simple_tag
def icon(name, **attrs):
    """Render an inline SVG icon.
 
    Optional keyword arguments:
        class        CSS classes (defaults to ``icon``)
        size         any CSS length, e.g. ``"1.5rem"`` or ``"32"``
        stroke_width stroke weight, defaults to ``2``
        label        accessible name; without it the icon is hidden from
                     assistive technology (correct for decorative icons)
    """
    body = ICONS.get(name)
    if body is None:
        return ""
 
    css_class = escape(attrs.get("class", "icon"))
    stroke_width = escape(str(attrs.get("stroke_width", 2)))
    label = attrs.get("label")
    size = attrs.get("size")
 
    style = ""
    if size:
        length = str(size)
        if length.isdigit():
            length += "px"
        style = f' style="--icon-size:{escape(length)}"'
 
    if label:
        a11y = f' role="img" aria-label="{escape(str(label))}"'
    else:
        a11y = ' aria-hidden="true" focusable="false"'
 
    if name in FILLED:
        paint = 'fill="currentColor" stroke="none"'
    else:
        paint = (
            f'fill="none" stroke="currentColor" stroke-width="{stroke_width}" '
            'stroke-linecap="round" stroke-linejoin="round"'
        )
 
    return mark_safe(
        f'<svg class="{css_class}" viewBox="0 0 24 24" {paint}{style}{a11y}>'
        f"{body}</svg>"
    )