"""
Example: Using the main PPTAgent class
"""

from src.agent import PPTAgent
from pathlib import Path


def demo_simple_generation():
    """Demonstrate simple PPT generation"""
    print("=" * 70)
    print("PPTAgent 简单示例")
    print("=" * 70)

    # Initialize agent (using mock LLM for demo)
    from unittest.mock import Mock
    
    # Create mock LLM
    mock_llm = Mock()
    mock_llm.model = "gpt-4-demo"
    mock_llm.generate_json.return_value = {
        "title": "AI技术分享",
        "author": "技术讲师",
        "template_id": "simple_001",
        "slides": [
            {
                "slide_number": 1,
                "layout_type": "cover",
                "content": {
                    "title": "AI技术分享",
                    "subtitle": "探索人工智能的未来",
                    "author": "技术讲师",
                },
            },
            {
                "slide_number": 2,
                "layout_type": "toc",
                "content": {
                    "title": "目录",
                    "items": ["AI概述", "核心技术", "应用场景"],
                },
            },
            {
                "slide_number": 3,
                "layout_type": "content_single",
                "content": {
                    "title": "AI概述",
                    "content": "人工智能（AI）是计算机科学的一个分支\n\n"
                    "• 机器学习\n"
                    "• 深度学习\n"
                    "• 自然语言处理",
                },
            },
            {
                "slide_number": 4,
                "layout_type": "ending",
                "content": {"message": "感谢观看！"},
            },
        ],
    }

    # Create agent with mock LLM
    from src.outline.generator import OutlineGenerator
    
    outline_gen = OutlineGenerator(llm_client=mock_llm)
    agent = PPTAgent(llm_provider="openai")
    agent.outline_generator = outline_gen  # Replace with mock

    print("\n📝 生成PPT...")
    print("主题：AI技术分享\n")

    # Generate presentation
    try:
        result = agent.generate_presentation(
            user_input="AI技术分享",
            author="技术讲师",
            output_dir=Path("examples/generated"),
        )

        print("✅ 生成成功！")
        print(f"\nPPT文件：{result['ppt']}")
        print(f"大纲文件：{result['outline']}")
        print(f"文件大小：{result['ppt'].stat().st_size / 1024:.1f} KB")

    except Exception as e:
        print(f"❌ 生成失败：{e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)


def demo_template_selection():
    """Demonstrate template listing"""
    print("\n" + "=" * 70)
    print("模板列表示例")
    print("=" * 70)

    agent = PPTAgent()

    print("\n可用模板：\n")
    templates = agent.list_templates()

    for i, template in enumerate(templates, 1):
        print(f"{i}. {template['template_name']}")
        print(f"   ID: {template['template_id']}")
        print(f"   描述: {template.get('description', 'N/A')}")
        print()

    print("=" * 70)


def main():
    """Run all demos"""
    demo_template_selection()
    demo_simple_generation()

    print("\n💡 提示：")
    print("  配置真实API密钥后，可以使用真实LLM生成PPT")
    print("  示例：agent.generate_presentation('年终总结', author='张三')")


if __name__ == "__main__":
    main()
