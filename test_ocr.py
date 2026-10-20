
from PIL import Image
from main import preprocess_image, clean_ocr_text

image = Image.open("ttest2.png").convert("RGB")
processed = preprocess_image(image)

print("\n--- CONFIDENCE-FILTERED OCR ---")
print(clean_ocr_text(processed))
