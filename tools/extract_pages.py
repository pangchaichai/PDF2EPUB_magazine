#!/usr/bin/env python3
"""
PDF Page Extractor - 从原始 PDF 中提取指定页面生成轻量测试样本

用法:
    python tools/extract_pages.py <输入PDF> <起始页> <结束页> [输出PDF]

示例:
    # 提取第 8 至第 10 页，保存为 test_sample.pdf
    python tools/extract_pages.py magazine.pdf 8 10 test_sample.pdf

    # 若未指定输出文件名，则自动生成 extracted_p8-10.pdf
    python tools/extract_pages.py magazine.pdf 8 10
"""

import sys
import os
from pathlib import Path

# 将项目根目录添加到 Python 路径，以便能导入 src 模块（如果需要）
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import fitz  # PyMuPDF
except ImportError:
    print("❌ 未找到 PyMuPDF 库，请先安装：pip install PyMuPDF")
    sys.exit(1)


def extract_pages(input_pdf: str, start_page: int, end_page: int, output_pdf: str = None):
    """
    从原始 PDF 中提取指定页码范围，生成新的 PDF 文件。

    Args:
        input_pdf: 输入的 PDF 文件路径
        start_page: 起始页码（从 1 开始计数）
        end_page: 结束页码（包含）
        output_pdf: 输出的 PDF 文件路径（可选）
    """
    if not os.path.exists(input_pdf):
        print(f"❌ 输入文件不存在: {input_pdf}")
        sys.exit(1)

    # 打开原始 PDF
    src = fitz.open(input_pdf)
    total = len(src)

    # 转换为 0-based 索引
    start_idx = start_page - 1
    end_idx = end_page - 1

    # 验证页码范围
    if start_idx < 0 or end_idx >= total or start_idx > end_idx:
        print(f"❌ 页码范围无效。总页数: {total}")
        src.close()
        sys.exit(1)

    # 默认输出文件名
    if output_pdf is None:
        base_name = Path(input_pdf).stem
        output_pdf = f"{base_name}_p{start_page}-{end_page}.pdf"

    # 创建新 PDF 并插入指定页面
    dst = fitz.open()
    for i in range(start_idx, end_idx + 1):
        dst.insert_pdf(src, from_page=i, to_page=i)

    dst.save(output_pdf)
    dst.close()
    src.close()

    print(f"✅ 成功提取第 {start_page}-{end_page} 页（共 {end_page - start_page + 1} 页）")
    print(f"   保存为: {output_pdf}")


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    input_pdf = sys.argv[1]
    try:
        start = int(sys.argv[2])
        end = int(sys.argv[3])
    except ValueError:
        print("❌ 起始页和结束页必须是整数")
        sys.exit(1)

    output = sys.argv[4] if len(sys.argv) > 4 else None

    extract_pages(input_pdf, start, end, output)


if __name__ == "__main__":
    main()
