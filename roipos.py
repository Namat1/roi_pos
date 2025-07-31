import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import pytesseract
import shutil

# Sicherstellen, dass Tesseract verfügbar ist
TESS_CMD = shutil.which("tesseract")
if TESS_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESS_CMD
else:
    st.error("❌ Tesseract nicht installiert. Bitte `tesseract-ocr` in packages.txt angeben.")
    st.stop()

st.set_page_config(layout="wide")
st.title("📄 PDF anzeigen & Rechteck für OCR ziehen")

pdf_file = st.file_uploader("PDF hochladen", type=["pdf"])
dpi = st.slider("DPI zum Rendern", 72, 300, 150)

if not pdf_file:
    st.stop()

# Seite rendern
pages = convert_from_bytes(pdf_file.read(), dpi=dpi)
img = pages[0].convert("RGB")

# Optional: verkleinern für Anzeige
preview = img.copy()
preview.thumbnail((1000, 1500))  # Vorschaugröße
w, h = preview.size

# Canvas anzeigen
canvas_result = st_canvas(
    background_image=preview,
    height=h,
    width=w,
    drawing_mode="rect",
    stroke_color="red",
    stroke_width=2,
    key="ocr-canvas"
)

# Wenn ein Rechteck gezeichnet wurde
if canvas_result.json_data and canvas_result.json_data["objects"]:
    rect = canvas_result.json_data["objects"][-1]
    x = int(rect["left"])
    y = int(rect["top"])
    rw = int(rect["width"])
    rh = int(rect["height"])

    st.success(f"📐 Gezogenes Rechteck: (x={x}, y={y}, w={rw}, h={rh})")

    # Entsprechend Originalgröße hochskalieren
    scale_x = img.width / w
    scale_y = img.height / h

    orig_x = int(x * scale_x)
    orig_y = int(y * scale_y)
    orig_w = int(rw * scale_x)
    orig_h = int(rh * scale_y)

    roi_img = img.crop((orig_x, orig_y, orig_x + orig_w, orig_y + orig_h))

    st.image(roi_img, caption="Ausgeschnittener Bereich (Originalgröße)")

    text = pytesseract.image_to_string(roi_img, lang="deu+eng")
    st.markdown("### 🧾 OCR-Text:")
    st.code(text.strip() or "(kein Text erkannt)")
else:
    st.info("Bitte ein Rechteck auf dem PDF ziehen.")
