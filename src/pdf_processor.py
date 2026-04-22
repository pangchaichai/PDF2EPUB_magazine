import io
import fitz
from PIL import Image
import base64
from src.ai_client import AIClient
from src.utils import stitch_across_pages


class PDFProcessor:
    def __init__(self, config, model_type="deepseek-vl2"):
        self.config = config
        self.dpi = config["conversion"]["image_dpi"]
        self.model_type = model_type
        self.ai_client = AIClient(config, model_type=model_type)

    def get_page_count(self, pdf_path):
        doc = fitz.open(pdf_path)
        count = len(doc)
        doc.close()
        return count

    def _page_to_base64(self, pdf_path, page_num):
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_num)
        zoom = self.dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        doc.close()
        return img_base64

    def process_page(self, pdf_path, page_num, total_pages, style_hint=None):
        img_b64 = self._page_to_base64(pdf_path, page_num)
        md = self.ai_client.analyze_page(img_b64, page_num, total_pages, style_hint=style_hint)
        return md

    def stitch_pages(self, page_mds):
        return stitch_across_pages(page_mds, self.ai_client.client, self.config)
