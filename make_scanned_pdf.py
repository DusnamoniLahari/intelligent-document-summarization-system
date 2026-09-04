import pymupdf
from PIL import Image
from io import BytesIO

input_pdf = r"C:\Users\lahar\my personal\capstone\Traffic management csp doc1.pdf"
output_pdf = "Traffic_management_OCR_test.pdf"

doc = pymupdf.open(input_pdf)
new_pdf = pymupdf.open()

for page in doc:
    pix = page.get_pixmap(dpi=150)

    image_bytes = pix.tobytes("png")
    image = Image.open(BytesIO(image_bytes)).convert("RGB")

    img_bytes = BytesIO()
    image.save(img_bytes, format="JPEG", quality=90)

    new_page = new_pdf.new_page(
        width=pix.width,
        height=pix.height
    )

    new_page.insert_image(
        new_page.rect,
        stream=img_bytes.getvalue()
    )

new_pdf.save(output_pdf)

doc.close()
new_pdf.close()

print("Created:", output_pdf)