
def svg_hexgrid(content: list[str], bg_color: str = "#0077be"):
  return f"""
  <svg viewBox="0 0 10 10" style="background-color: {bg_color};">
    <defs>
      <path id="hexagon" d="M 1 0 L 0.5 -0.87 L -0.5 -0.87 L -1 0 L -0.5 0.87 L 0.5 0.87 Z" transform="rotate(30)" />
    </defs>

    <g id="hexgrid">
    """ + \
      "\n".join(content) + \
      """
    </g>
  </svg>
  """


def svg_hexagon(x: float, y: float, color: str, size: float = 1.0, stroke_color: str = "black", stroke_width: float = 0.03) -> str:
  return f"<use href='#hexagon' x='{x}' y='{y}' fill='{color}' stroke='{stroke_color}' stroke-width='{stroke_width}' transform='scale({size})' />"


def svg_text(x: float, y: float, text: str, color: str = "white", font_size: float = 0.3, text_anchor: str = "middle") -> str:
  return f"<text x='{x}' y='{y}' text-anchor='{text_anchor}' font-size='{font_size}' fill='{color}'>{text}</text>"

def svg_rect(x: float, y: float, width: float, height: float, color: str = "white", angle: float = 0) -> str:
  return f"<rect x='{x}' y='{y}' width='{width}' height='{height}' fill='{color}' transform='rotate({angle})' />"
