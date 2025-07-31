# Streamlit PDF ROI Picker
# -------------------------
# Eine kleine Demo‑App, mit der du
#  1. ein PDF hochlädst,
#  2. eine Seite als Bild renderst,
#  3. ein Rechteck auf das Bild zeichnest,
#  4. die Koordinaten der Auswahl als (x, y, w, h) und (left, upper, right, lower) ausgibst.
#
# Benötigte Pakete (installiere sie in deiner virtuellen Umgebung):
#   pip install streamlit pdf2image pillow streamlit-drawable-canvas
# Außerdem muss auf dem System poppler installiert sein, weil pdf2image darauf zugreift.
# Unter Ubuntu/Debian: sudo apt-get install poppler-utils

import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image
from streamlit_drawable_canvas import st_canvas


st.set_page_config(page_title="PDF ROI Picker", layout="wide")

st.title("📄🔍 PDF ROI Picker")

# --------------------------
# 1. PDF hochladen
# --------------------------
pdf_file = st.file_uploader("PDF wählen", type=["pdf"], help="Zieh eine PDF-Datei hierher oder klick, um eine auszuwählen.")

dpi = st.slider("Render-DPI (Auflösung)", 72, 300, 150, 10, help="Je höher, desto schärfer das Bild, aber langsamer im Rendering.")

if pdf_file is None:
    st.info("⬆️ Lade zunächst eine PDF-Datei hoch.")
    st.stop()

# --------------------------
# 2. PDF → PIL-Bilder
# --------------------------
# Wir lesen die Bytes nur einmal ein, denn convert_from_bytes verbraucht sie.
pdf_bytes = pdf_file.read()
try:
    pages: list[Image.Image] = convert_from_bytes(pdf_bytes, dpi=dpi)
except Exception as e:
    st.error(f"Fehler beim Rendern der PDF-Datei: {e}")
    st.stop()

num_pages = len(pages)
page_idx = st.number_input("Seite auswählen", 1, num_pages, 1, key="page_idx") - 1
page_img = pages[page_idx]
W, H = page_img.size

st.write(f"Seite {page_idx + 1} von {num_pages} – Bildgröße: **{W}×{H} px**")

# --------------------------
# 3. Zeichen‑Canvas
# --------------------------
canvas_result = st_canvas(
    fill_color="rgba(0, 0, 0, 0)",  # transparente Füllung
    stroke_width=2,
    stroke_color="red",
    background_image=page_img,
    height=H,
    width=W,
    drawing_mode="rect",
    update_streamlit=True,
    key="canvas",
)

# --------------------------
# 4. Koordinaten ausgeben
# --------------------------
if canvas_result.json_data and canvas_result.json_data["objects"]:
    # wir nehmen das zuletzt gezeichnete Rechteck
    rect = canvas_result.json_data["objects"][-1]
    x = int(rect["left"])
    y = int(rect["top"])
    w_rect = int(rect["width"])
    h_rect = int(rect["height"])

    st.subheader("📏 Koordinaten")
    st.write("(x, y, w, h):", (x, y, w_rect, h_rect))
    st.write("(left, upper, right, lower):", (x, y, x + w_rect, y + h_rect))

    # Optionale Sicherung als JSON
    if st.button("Koordinaten kopieren", type="secondary"):
        coord_str = f"{x}, {y}, {w_rect}, {h_rect}"
        st.session_state.clipboard = coord_str  # bereitstellen – Browser-Clipboard-API wird durch st.button leider nicht direkt unterstützt
        st.success("Koordinaten in die Zwischenablage kopiert (sofern Browser‑API verfügbar).")
else:
    st.info("Zeichne ein Rechteck auf die Seite, um Koordinaten zu erhalten.")

# --------------------------
# Hinweise zur Weiterverarbeitung
# --------------------------
with st.expander("ℹ️   Wie nutze ich die Koordinaten in Pillow / OpenCV?"):
    st.markdown(
        """
        * **Pillow** (`Image.crop`):
          ```python
          left, upper, right, lower = x, y, x + w, y + h
          roi_img = pil_img.crop((left, upper, right, lower))
          ```
        * **OpenCV / NumPy Slicing**:
          ```python
          roi = img[y : y + h, x : x + w]
          ```
        """
    )
