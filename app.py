from flask import Flask, request, send_file
import cv2
import numpy as np
from PIL import Image
import potrace
import io

app = Flask(__name__)

def vectorize_image(file):
    # Leer imagen
    image = Image.open(file).convert("RGB")
    img_np = np.array(image)

    # Escala de grises
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

    # Suavizado (bordes más limpios)
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    # Binarización
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Invertir (potrace trabaja mejor así)
    thresh = 255 - thresh

    # Vectorizar
    bmp = potrace.Bitmap(thresh)
    path = bmp.trace()

    # Crear SVG
    svg_io = io.StringIO()
    svg_io.write('<svg xmlns="http://www.w3.org/2000/svg">')
    for curve in path:
        svg_io.write('<path d="')
        for segment in curve:
            svg_io.write(f"M {segment.start_point[0]} {segment.start_point[1]} ")
            svg_io.write(f"L {segment.end_point[0]} {segment.end_point[1]} ")
        svg_io.write('" fill="black"/>')
    svg_io.write('</svg>')

    # PNG 300 DPI
    png_io = io.BytesIO()
    image.save(png_io, format="PNG", dpi=(300,300))

    return svg_io.getvalue(), png_io

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    svg, png = vectorize_image(file)

    return {
        "svg": svg,
        "png": png.getvalue().hex()
    }

if __name__ == "__main__":
    app.run()
