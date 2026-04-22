import os
import base64
from pathlib import Path
from openai import OpenAI

# 尝试导入 Gemini SDK（可选）
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class AIClient:
    """支持 DeepSeek-VL2、GPT-4o-mini 和 Gemini 1.5 Pro 的统一 AI 客户端"""

    def __init__(self, config, model_type="deepseek-vl2"):
        self.config = config
        self.model_type = model_type
        self.max_tokens = config["conversion"]["max_tokens"]
        self.temperature = config["conversion"]["temperature"]

        # 模板目录
        self.template_dir = Path(__file__).parent / "templates"
        self.core_rules = self._load_core_rules()

        # 初始化 API 客户端
        if model_type == "deepseek-vl2":
            self.client = OpenAI(
                api_key=config["deepseek"]["api_key"],
                base_url=config["deepseek"]["base_url"],
            )
            self.model = config["deepseek"]["model"]
        elif model_type == "gpt-4o-mini":
            self.client = OpenAI(
                api_key=config["openai"]["api_key"],
                base_url=config["openai"].get("base_url", "https://api.openai.com/v1"),
            )
            self.model = config["openai"]["model"]
        elif model_type == "gemini-1.5-pro":
            if not GEMINI_AVAILABLE:
                raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")
            genai.configure(api_key=config["gemini"]["api_key"])
            self.model = config["gemini"]["model"]
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    def _load_core_rules(self):
        """加载静态核心规则"""
        core_path = self.template_dir / "core_rules.txt"
        if core_path.exists():
            return core_path.read_text(encoding="utf-8")
        else:
            return "You are an expert publication layout analyst..."

    def _load_style_template(self, style_name):
        """加载指定风格的模板（如果存在）"""
        if not style_name:
            return None
        template_path = self.template_dir / f"{style_name}.txt"
        custom_path = self.template_dir / "custom" / f"{style_name}.txt"
        if custom_path.exists():
            return custom_path.read_text(encoding="utf-8")
        elif template_path.exists():
            return template_path.read_text(encoding="utf-8")
        else:
            return None

    def _build_system_prompt(self, style_name=None):
        """动态组装 System Prompt = 核心规则 + 可选风格模板"""
        prompt_parts = [self.core_rules]

        if style_name:
            template = self._load_style_template(style_name)
            if template:
                prompt_parts.append(f"\n\n## 🎨 STYLE-SPECIFIC GUIDANCE\n{template}")

        prompt_parts.append(
            "\n\n---\n**FINAL REMINDER:** Output only valid Markdown. "
            "No conversational text, no JSON, no explanations."
        )
        return "\n".join(prompt_parts)

    def analyze_page(self, image_base64: str, page_num: int, total_pages: int, style_hint: str = None) -> str:
        """分析单页内容，可指定风格提示"""
        system_prompt = self._build_system_prompt(style_hint)

        if self.model_type in ("deepseek-vl2", "gpt-4o-mini"):
            return self._analyze_with_openai(image_base64, page_num, total_pages, system_prompt)
        elif self.model_type == "gemini-1.5-pro":
            return self._analyze_with_gemini(image_base64, page_num, total_pages, system_prompt)

    def _analyze_with_openai(self, image_base64, page_num, total_pages, system_prompt):
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Page {page_num + 1} of {total_pages}. Extract content following the rules strictly.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                    },
                ],
            },
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return response.choices[0].message.content

    def _analyze_with_gemini(self, image_base64, page_num, total_pages, system_prompt):
        import io
        from PIL import Image

        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        model = genai.GenerativeModel(self.model)
        prompt = f"{system_prompt}\n\nPage {page_num + 1} of {total_pages}. Extract content following the rules strictly."
        response = model.generate_content([prompt, image])
        return response.text


# ============================================================
# 核心规则（定义在代码中作为回退，实际从 core_rules.txt 加载）
# ============================================================
