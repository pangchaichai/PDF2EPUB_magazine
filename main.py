#!/usr/bin/env python3
"""
PDF2EPUB_magazine - Main Entry Point
"""

import argparse
import json
import yaml
from pathlib import Path
from src.pdf_processor import PDFProcessor
from src.epub_builder import EPUBBuilder
from src.style_fingerprinter import StyleFingerprinter
from src.style_learner import StyleLearner
from tqdm import tqdm


def load_config(config_path="config.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Convert complex PDF magazine to EPUB using AI vision models."
    )
    parser.add_argument("--input", "-i", required=True, help="Path to input PDF file")
    parser.add_argument("--output", "-o", required=True, help="Path to output EPUB file")
    parser.add_argument("--config", "-c", default="config.yaml", help="Path to config file")
    parser.add_argument(
        "--model", "-m",
        choices=["deepseek-vl2", "gpt-4o-mini", "gemini-1.5-pro"],
        help="Override model selection in config file"
    )
    parser.add_argument("--style", "-s", help="Manually specify style template (e.g., BRN, ECON, BBW)")
    parser.add_argument("--auto-style", action="store_true", help="Automatically detect magazine style")
    parser.add_argument("--learn", help="Path to a JSON file containing corrections for learning")
    args = parser.parse_args()

    config = load_config(args.config)

    # 学习模式（不进行转换，仅生成模板）
    if args.learn:
        if not Path(args.learn).exists():
            print(f"❌ File not found: {args.learn}")
            return
        learner = StyleLearner(config)
        with open(args.learn, 'r', encoding='utf-8') as f:
            corrections = json.load(f)
        for idx, corr in enumerate(corrections):
            print(f"📚 Learning from correction {idx+1}/{len(corrections)}...")
            snippet, path = learner.learn_from_correction(
                corr["image_base64"],
                corr["ai_output"],
                corr["corrected"],
                corr.get("style_name")
            )
            print(f"✅ Learned template saved to {path}")
        print("🎓 Learning completed.")
        return

    # 确定使用的模型
    model_type = args.model if args.model else config.get("model_type", "deepseek-vl2")
    print(f"🤖 Using model: {model_type}")

    # 确定风格模板
    style_hint = args.style
    if args.auto_style and not style_hint:
        print("🔍 Auto-detecting magazine style...")
        fingerprinter = StyleFingerprinter(args.input)
        style_hint = fingerprinter.identify_style()
        print(f"   Detected style: {style_hint or 'generic (no specific template)'}")

    # 初始化处理器
    processor = PDFProcessor(config, model_type=model_type)

    print(f"🚀 Starting conversion of {args.input}")
    page_mds = []
    total_pages = processor.get_page_count(args.input)

    for page_num in tqdm(range(total_pages), desc="Processing pages"):
        md_content = processor.process_page(
            args.input, page_num, total_pages, style_hint=style_hint
        )
        page_mds.append(md_content)

    # 跨页拼接
    print("🧵 Stitching across pages...")
    final_md = processor.stitch_pages(page_mds)

    # 生成 EPUB
    print("📖 Building EPUB...")
    builder = EPUBBuilder(config)
    title = Path(args.input).stem
    builder.create_epub(final_md, args.output, title=title)

    print(f"✅ Successfully created {args.output}")


if __name__ == "__main__":
    main()
