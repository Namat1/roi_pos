import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image
import pytesseract

st.set_page_config(layout="centered")
st.title("🔍 OCR-Vorschau für Namensfeld")

# Datei-Upload
pdf_file = st.file_uploader("📄 Dienstplan-PDF hochladen", type=["pdf"])
dpi = st.slider("DPI für Rendern", 72, 300, 150)

# ROI-Koordinaten für "Philipp Auer" (unten rechts bei 150 dpi)
roi_box = (920, 1630, 240, 60)  # (x, y, w, h)

if pdf_file:
    # PDF in Bild konvertieren
    pages = convert_from_bytes(pdf_file.read(), dpi=dpi)
    img = pages[0].convert("RGB")

    # ROI berechnen und ausschneiden
    x, y, w, h = roi_box
    scale = dpi / 150  # Skalierungsfaktor bei anderer DPI
    x, y, w, h = int(x * scale), int(y * scale), int(w * scale), int(h * scale)
    cropped = img.crop((x, y, x + w, y + h))

    # Anzeige
    st.image(img, caption="Gesamte PDF-Seite", use_column_width=True)
    st.markdown("---")
    st.image(cropped, caption=f"ROI ({x}, {y}, {w}, {h})", use_column_width=False)

    # OCR-Vorschau
    try:
        text = pytesseract.image_to_string(cropped, lang="deu+eng")
    except Exception:
        text = pytesseract.image_to_string(cropped)

    st.markdown("### 🧾 OCR-Text im markierten Bereich:")
    st.code(text.strip() or "(Kein Text erkannt)")
