import webcolors
from webcolors._definitions import _CSS3_HEX_TO_NAMES

def hex_to_name(hex_code):
    try:
        return webcolors.hex_to_name(hex_code, spec='css3').upper()
    except ValueError:
        try:
            rgb = webcolors.hex_to_rgb(hex_code)
        except ValueError:
            return hex_code.upper()
        closest_name = min(
            _CSS3_HEX_TO_NAMES.items(),
            key=lambda item: sum((a - b) ** 2 for a, b in zip(rgb, webcolors.hex_to_rgb(item[0])))
        )
        return closest_name[1].upper()