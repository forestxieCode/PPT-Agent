"""
Example: Full PPT generation pipeline
"""

import json
from pathlib import Path
from unittest.mock import Mock

from src.outline.generator import OutlineGenerator
from src.generator.ppt_generator import PPTGenerator
from src.utils.file_utils import ensure_dir


def create_mock_llm_client():
    """Create a mock LLM client for demonstration"""
    client = Mock()
    client.model = "gpt-4-demo"

    # Mock response for a simple presentation
    client.generate_json.return_value = {
        "title": "Python快速入门",
        "author": "技术讲师",
        "template_id": "business_001",  # Use business template which has more layouts
        "slides": [
            {
                "slide_number": 1,
                "layout_type": "cover",
                "content": {
                    "title": "Python快速入门",
                    "subtitle": "从零开始学习Python编程",
                    "author": "技术讲师 | 编程教育部",
                },
            },
            {
                "slide_number": 2,
                "layout_type": "toc",
                "content": {
                    "title": "课程大纲",
                    "items": [
                        "Python简介",
                        "开发环境搭建",
                        "基础语法",
                        "数据类型",
                        "控制流程",
                        "函数与模块",
                    ],
                },
            },
            {
                "slide_number": 3,
                "layout_type": "content_single",
                "content": {
                    "title": "Python简介",
                    "content": "Python是一种解释型、面向对象的高级编程语言\n\n"
                    "• 简洁易读的语法\n"
                    "• 丰富的标准库\n"
                    "• 强大的第三方生态\n"
                    "• 广泛的应用领域：Web开发、数据科学、AI等",
                },
            },
            {
                "slide_number": 4,
                "layout_type": "content_single",
                "content": {
                    "title": "开发环境搭建",
                    "content": "准备Python开发环境\n\n"
                    "1. 下载并安装Python（推荐3.11+）\n"
                    "2. 配置环境变量\n"
                    "3. 安装IDE（VS Code / PyCharm）\n"
                    "4. 验证安装：python --version",
                },
            },
            {
                "slide_number": 5,
                "layout_type": "content_single",
                "content": {
                    "title": "基础语法示例",
                    "content": "Python代码示例\n\n"
                    "# 变量定义\n"
                    "name = 'Python'\n"
                    "version = 3.11\n\n"
                    "# 打印输出\n"
                    "print(f'Hello, {name} {version}!')\n\n"
                    "# 条件判断\n"
                    "if version >= 3.0:\n"
                    "    print('使用Python 3')",
                },
            },
            {
                "slide_number": 6,
                "layout_type": "content_two_column",
                "content": {
                    "title": "数据类型",
                    "content_left": "基本类型\n\n"
                    "• 整数 (int)\n"
                    "• 浮点数 (float)\n"
                    "• 字符串 (str)\n"
                    "• 布尔值 (bool)",
                    "content_right": "容器类型\n\n"
                    "• 列表 (list)\n"
                    "• 元组 (tuple)\n"
                    "• 字典 (dict)\n"
                    "• 集合 (set)",
                },
            },
            {
                "slide_number": 7,
                "layout_type": "content_single",
                "content": {
                    "title": "控制流程",
                    "content": "控制程序执行流程\n\n"
                    "• 条件语句：if / elif / else\n"
                    "• 循环语句：for / while\n"
                    "• 跳转语句：break / continue\n"
                    "• 异常处理：try / except / finally",
                },
            },
            {
                "slide_number": 8,
                "layout_type": "content_single",
                "content": {
                    "title": "函数与模块",
                    "content": "代码复用与组织\n\n"
                    "函数定义：\n"
                    "def greet(name):\n"
                    "    return f'你好，{name}！'\n\n"
                    "模块导入：\n"
                    "import math\n"
                    "from datetime import datetime",
                },
            },
            {
                "slide_number": 9,
                "layout_type": "ending",
                "content": {"message": "感谢学习！", "contact": "继续探索Python的精彩世界"},
            },
        ],
    }

    return client


def main():
    """Demonstrate full PPT generation pipeline"""
    print("=" * 70)
    print("完整PPT生成流程演示")
    print("=" * 70)

    # Step 1: Generate outline
    print("\n📝 步骤1：生成PPT大纲")
    print("-" * 70)

    mock_llm = create_mock_llm_client()
    outline_generator = OutlineGenerator(llm_client=mock_llm)

    outline = outline_generator.generate_outline(
        user_input="Python快速入门教程", author="技术讲师", max_slides=10
    )

    print(f"✅ 大纲生成成功")
    print(f"   标题：{outline.title}")
    print(f"   作者：{outline.author}")
    print(f"   模板：{outline.template_id}")
    print(f"   总页数：{len(outline.slides)}")

    # Step 2: Save outline
    print("\n💾 步骤2：保存大纲到文件")
    print("-" * 70)

    output_dir = Path("examples/generated")
    ensure_dir(output_dir)

    outline_path = output_dir / "outline_python_tutorial.json"
    outline_dict = outline.model_dump(mode="json")
    outline_dict["metadata"]["generated_at"] = outline.metadata.generated_at.isoformat()

    with open(outline_path, "w", encoding="utf-8") as f:
        json.dump(outline_dict, f, ensure_ascii=False, indent=2)

    print(f"✅ 大纲已保存：{outline_path}")

    # Step 3: Generate PPT
    print("\n🎨 步骤3：生成PPT文件")
    print("-" * 70)

    ppt_generator = PPTGenerator()

    try:
        ppt_path = ppt_generator.generate(
            outline=outline, output_path=output_dir / "python_tutorial.pptx"
        )

        print(f"✅ PPT生成成功！")
        print(f"   文件位置：{ppt_path}")
        print(f"   文件大小：{ppt_path.stat().st_size / 1024:.1f} KB")

        # Display slide details
        print("\n📊 幻灯片详情：")
        for slide in outline.slides:
            layout_type = slide.layout_type
            title = slide.content.get("title", "")
            if not title:
                title = slide.content.get("message", "封面")
            print(f"   第{slide.slide_number}页：{layout_type:20s} - {title}")

    except Exception as e:
        print(f"❌ PPT生成失败：{e}")
        import traceback

        traceback.print_exc()
        return

    # Summary
    print("\n" + "=" * 70)
    print("✨ 完整流程演示完成！")
    print("=" * 70)
    print("\n生成的文件：")
    print(f"  1. {outline_path}")
    print(f"  2. {ppt_path}")
    print("\n💡 提示：")
    print("  • 使用PowerPoint或WPS打开生成的PPT文件")
    print("  • 可以在大纲JSON中修改内容后重新生成")
    print("  • 配置真实LLM后可以生成更多样化的内容")
    print("=" * 70)


if __name__ == "__main__":
    main()
