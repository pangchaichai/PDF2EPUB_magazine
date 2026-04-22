# PDF2EPUB_magazine by Pang_Jeff
A tool for users to convert .pdf files to .epub or .mobi files, such as magazines or ebooks. It can make reading more comfortable and easily.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个基于AI多模态大模型的智能PDF杂志转换工具，专门解决复杂排版（多栏、图文混排、艺术字体）的PDF转EPUB难题。

## ⚠️ 法律声明

本项目仅供**个人学习与研究**使用。使用本工具前，您必须确保：

1. 您拥有所转换PDF文件的合法副本（例如通过正规渠道付费订阅获取）。
2. 转换后的EPUB文件仅用于个人在移动设备上阅读，不得以任何形式传播、分享或用于商业目的。
3. 您已知晓并同意，任何违反版权法的行为（包括但不限于破解DRM、分发盗版内容）均与项目作者无关，由使用者自行承担全部法律责任。

本项目不包含任何DRM破解功能，也不鼓励或支持任何侵犯知识产权的行为。

## ✨ 特性

- **版面智能理解**：利用多模态大模型（DeepSeek-VL2 / GPT-4o-mini / Gemini 1.5 Pro）分析页面布局，精准恢复阅读顺序。
- **复杂排版支持**：完美处理多栏、侧边栏、跨页文章、艺术字标题等。
- **自我进化能力**：支持从用户修正中学习，生成新的风格模板（Style Learner）。
- **自动风格识别**：自动检测杂志的视觉特征（栏数、表格密度、图片占比），匹配合适的解析模板。
- **多模型切换**：命令行一键切换 DeepSeek-VL2、GPT-4o-mini、Gemini 1.5 Pro。
- **低成本高效率**：默认使用 DeepSeek-VL2，处理一本100页杂志成本仅约 $0.02。

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/yourusername/pdf-magazine-to-epub.git
cd pdf-magazine-to-epub
