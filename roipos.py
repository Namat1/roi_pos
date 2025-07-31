from pdf2image import convert_from_bytes
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import streamlit as st
import numpy as np

st.set_page_config(layout="wide")
st.title("🖼️ PDF-Anzeige mit ROI-Auswahl")

# Datei laden
pdf_bytes = st.file_uploader("PDF hochladen", type=["pdf"])
if not pdf_bytes:
    st.stop()

dpi = st.slider("DPI", 72, 300, 150)

# Rendern der Seite 1
try:
    pages = convert_from_bytes(pdf_bytes.read(), dpi=dpi)
    img = pages[0].convert("RGB")
except Exception as e:
    st.error(f"❌ Fehler beim Rendern der PDF-Seite: {e}")
    st.stop()

# Vorschaubild skalieren
preview = img.copy()
preview.thumbnail((600, 800))
img_np = np.array(preview)
h, w = img_np.shape[:2]
st.write(f"Größe der Vorschau: {w}×{h}")

# ✅ Trick: Übergabe über Dictionary, um ValueError zu vermeiden
canvas_kwargs = dict(
    height=h,
    width=w,
    drawing_mode="rect",
    stroke_color="red",
    stroke_width=2,
    key="canvas"
)

if isinstance(img_np, np.ndarray):
    canvas_kwargs["background_image"] = img_np

# Zeichenfläche anzeigen
canvas_result = st_canvas(**canvas_kwargs)

# Rechteck auslesen
if canvas_result.json_data and canvas_result.json_data["objects"]:
    rect = canvas_result.json_data["objects"][-1]
    x, y = int(rect["left"]), int(rect["top"])
    rw, rh = int(rect["width"]), int(rect["height"])
    st.success("📐 Koordinaten:")
    st.code(f"(x, y, w, h) = ({x}, {y}, {rw}, {rh})")
    st.code(f"(left, upper, right, lower) = ({x}, {y}, {x+rw}, {y+rh})")
else:
    st.info("Ziehe ein Rechteck, um Koordinaten zu erhalten.")
