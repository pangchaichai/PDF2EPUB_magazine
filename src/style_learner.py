import hashlib
import json
from pathlib import Path
from datetime import datetime
from openai import OpenAI


class StyleLearner:
    """从用户修正的样例中学习，生成新的风格模板片段"""

    def __init__(self, config):
        self.client = OpenAI(
            api_key=config["deepseek"]["api_key"],
            base_url=config["deepseek"]["base_url"],
        )
        self.template_dir = Path(__file__).parent / "templates"
        self.custom_dir = self.template_dir / "custom"
        self.custom_dir.mkdir(exist_ok=True)

    def learn_from_correction(self, original_image_base64, ai_output_md, corrected_md, style_name=None):
        if not style_name:
            img_hash = hashlib.md5(original_image_base64.encode()).hexdigest()[:8]
            style_name = f"learned_{img_hash}"

        learner_prompt = f"""
You are an expert in analyzing document layout extraction errors. You are given:

1. The original AI-generated Markdown (which contains errors).
2. The human-corrected Markdown (the ground truth).

Your task is to identify **what specific layout or style features caused the errors**, and generate a concise "style guidance" snippet that can be added to the system prompt to prevent similar errors in the future.

Focus on:
- Unique visual signatures of this publication (font usage, column structure, recurring elements).
- How certain elements were misclassified (e.g., sidebar mistaken as body, pull quote ignored).
- Specific handling instructions for this style.

Output ONLY the style guidance snippet in plain English, suitable for appending to a style template. Do not include any other text.

---

**Original AI Output (with errors):**
{ai_output_md}

**Corrected Output (ground truth):**
{corrected_md}

**Generated Style Guidance Snippet:**
"""

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": learner_prompt}],
            max_tokens=1000,
            temperature=0.2,
        )
        snippet = response.choices[0].message.content

        template_content = f"""## 🎨 STYLE TEMPLATE: {style_name} (Learned {datetime.now().strftime('%Y-%m-%d')})

### Visual Signature (Inferred from Correction)
[Automatically generated based on user correction]

### Style-Specific Handling
{snippet}

### Correction History
- Corrected on: {datetime.now().isoformat()}
"""
        template_path = self.custom_dir / f"{style_name}.txt"
        template_path.write_text(template_content, encoding="utf-8")

        meta_path = self.custom_dir / f"{style_name}.meta.json"
        meta_path.write_text(json.dumps({
            "created": datetime.now().isoformat(),
            "source": "user_correction",
            "correction_sample_hash": hashlib.md5(corrected_md.encode()).hexdigest()
        }), encoding="utf-8")

        return snippet, str(template_path)
