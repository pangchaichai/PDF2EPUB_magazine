import fitz
from collections import Counter


class StyleFingerprinter:
    """通过分析 PDF 页面的版面特征，自动识别杂志风格"""

    def __init__(self, pdf_path):
        self.doc = fitz.open(pdf_path)
        self.total_pages = len(self.doc)

    def _analyze_page(self, page_num):
        page = self.doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        text_blocks = [b for b in blocks if b["type"] == 0]

        col_count = self._estimate_columns(text_blocks)
        has_tables = self._detect_tables(page)
        image_density = self._calc_image_density(page)

        return {
            "columns": col_count,
            "has_tables": has_tables,
            "image_density": image_density,
        }

    def _estimate_columns(self, text_blocks):
        if not text_blocks:
            return 1
        x_coords = [b["bbox"][0] for b in text_blocks]
        if len(x_coords) < 5:
            return 1
        x_sorted = sorted(x_coords)
        gaps = [x_sorted[i+1] - x_sorted[i] for i in range(len(x_sorted)-1)]
        avg_gap = sum(gaps) / len(gaps) if gaps else 0
        large_gaps = [g for g in gaps if g > avg_gap * 2]
        return min(len(large_gaps) + 1, 4)

    def _detect_tables(self, page):
        blocks = page.get_text("dict")["blocks"]
        text_blocks = [b for b in blocks if b["type"] == 0]
        if len(text_blocks) > 10:
            y_coords = [b["bbox"][1] for b in text_blocks]
            y_counter = Counter([round(y, -1) for y in y_coords])
            if max(y_counter.values()) > 3:
                return True
        return False

    def _calc_image_density(self, page):
        blocks = page.get_text("dict")["blocks"]
        img_blocks = [b for b in blocks if b["type"] == 1]
        page_area = page.rect.width * page.rect.height
        img_area = sum(
            (b["bbox"][2]-b["bbox"][0]) * (b["bbox"][3]-b["bbox"][1])
            for b in img_blocks
        )
        return img_area / page_area if page_area else 0

    def identify_style(self, sample_pages=3):
        features = []
        for p in range(min(sample_pages, self.total_pages)):
            features.append(self._analyze_page(p))

        avg_cols = sum(f["columns"] for f in features) / len(features)
        table_ratio = sum(1 for f in features if f["has_tables"]) / len(features)
        avg_img_density = sum(f["image_density"] for f in features) / len(features)

        if table_ratio > 0.5 and avg_cols >= 3:
            return "BRN"
        elif avg_img_density > 0.3 and avg_cols <= 2:
            return "BBW"
        elif avg_cols >= 2 and table_ratio < 0.2:
            return "ECON"
        else:
            return None
