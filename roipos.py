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

# Vorschau kleiner skalieren
preview = img.copy()
preview.thumbnail((600, 800))  # Seite auf max 600 × 800 skalieren

try:
    img_np = np.array(preview)
    if img_np.ndim != 3 or img_np.shape[2] not in [3, 4]:
        raise ValueError(f"Ungültiges Bildformat: {img_np.shape}")
except Exception as e:
    st.error(f"❌ Fehler beim Umwandeln in NumPy: {e}")
    st.stop()

h, w = img_np.shape[:2]
st.write(f"Größe der Vorschau: {w}×{h}")

# Canvas mit geprüftem Bild
canvas_result = st_canvas(
    background_image=img_np,
    height=h,
    width=w,
    drawing_mode="rect",
    stroke_color="red",
    stroke_width=2,
    key="canvas"
)

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
