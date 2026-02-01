"""
Example: Outline generation with mocked LLM
"""

import json
from pathlib import Path
from unittest.mock import Mock

from src.outline.generator import OutlineGenerator
from src.outline.models import Outline
from src.utils.file_utils import save_json, ensure_dir


def create_mock_llm_client():
    """Create a mock LLM client for demonstration"""
    client = Mock()
    client.model = "gpt-4-demo"

    # Mock response for annual report
    client.generate_json.return_value = {
        "title": "2023年度工作述职报告",
        "author": "张三",
        "template_id": "business_001",
        "slides": [
            {
                "slide_number": 1,
                "layout_type": "cover",
                "content": {
                    "title": "2023年度工作述职报告",
                    "subtitle": "个人年度工作总结与展望",
                    "author": "张三 | 产品部",
                    "date": "2024年1月",
                },
                "notes": "开场白：感谢大家参加本次述职报告会",
            },
            {
                "slide_number": 2,
                "layout_type": "toc",
                "content": {
                    "title": "目录",
                    "items": [
                        "年度工作回顾",
                        "核心成果展示",
                        "数据与成绩",
                        "遇到的挑战",
                        "经验与收获",
                        "2024年工作计划",
                    ],
                },
            },
            {
                "slide_number": 3,
                "layout_type": "content_single",
                "content": {
                    "title": "年度工作回顾",
                    "content": "2023年主要工作内容：\n\n"
                    "• 负责XX产品的规划与迭代管理\n"
                    "• 完成5个重大项目的上线\n"
                    "• 团队协作与跨部门沟通\n"
                    "• 参与公司级战略项目",
                },
                "notes": "强调工作的广度和深度",
            },
            {
                "slide_number": 4,
                "layout_type": "content_two_column",
                "content": {
                    "title": "核心成果展示",
                    "content_left": "项目成果\n\n"
                    "• 项目A：用户增长30%\n"
                    "• 项目B：性能提升50%\n"
                    "• 项目C：成本降低20%",
                    "content_right": "个人成长\n\n"
                    "• 获得技术认证\n"
                    "• 发表技术文章3篇\n"
                    "• 内部分享5次",
                },
            },
            {
                "slide_number": 5,
                "layout_type": "content_single",
                "content": {
                    "title": "数据与成绩",
                    "content": "关键数据指标：\n\n"
                    "• 用户满意度：从85%提升至92%\n"
                    "• 项目按时交付率：95%\n"
                    "• 团队效率提升：35%\n"
                    "• 获得公司年度优秀员工称号",
                },
            },
            {
                "slide_number": 6,
                "layout_type": "content_single",
                "content": {
                    "title": "遇到的挑战",
                    "content": "主要挑战与应对：\n\n"
                    "• 技术难题：通过学习新技术和寻求专家帮助解决\n"
                    "• 资源紧张：优化工作流程，提高效率\n"
                    "• 需求变更：建立敏捷响应机制\n"
                    "• 跨部门协作：加强沟通，建立信任",
                },
            },
            {
                "slide_number": 7,
                "layout_type": "content_single",
                "content": {
                    "title": "经验与收获",
                    "content": "关键经验总结：\n\n"
                    "• 保持学习和成长的心态\n"
                    "• 注重团队协作和沟通\n"
                    "• 数据驱动决策\n"
                    "• 持续优化工作方法\n"
                    "• 关注用户价值",
                },
            },
            {
                "slide_number": 8,
                "layout_type": "content_single",
                "content": {
                    "title": "2024年工作计划",
                    "content": "新一年的目标与规划：\n\n"
                    "• 推动XX重点项目落地\n"
                    "• 提升团队技术能力\n"
                    "• 探索AI技术应用\n"
                    "• 深化用户研究\n"
                    "• 个人技能提升计划",
                },
            },
            {
                "slide_number": 9,
                "layout_type": "ending",
                "content": {
                    "message": "感谢聆听！",
                    "contact": "如有问题欢迎交流讨论",
                },
            },
        ],
    }

    return client


def main():
    """Demonstrate outline generation"""
    print("=" * 70)
    print("PPT大纲生成示例 (Mock模式)")
    print("=" * 70)

    # Create mock LLM client
    mock_llm = create_mock_llm_client()

    # Initialize generator with mock client
    generator = OutlineGenerator(llm_client=mock_llm)

    # Generate outline
    print("\n📝 生成PPT大纲...")
    print("主题：年终述职报告\n")

    outline = generator.generate_outline(
        user_input="年终述职报告",
        author="张三",
        max_slides=10,
        temperature=0.7,
    )

    # Display outline summary
    print(f"✅ 大纲生成成功！\n")
    print(f"标题：{outline.title}")
    print(f"作者：{outline.author}")
    print(f"模板：{outline.template_id}")
    print(f"总页数：{len(outline.slides)}")
    print(f"生成时间：{outline.metadata.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"使用模型：{outline.metadata.llm_model}\n")

    # Display slide details
    print("幻灯片详情：")
    print("-" * 70)
    for slide in outline.slides:
        print(f"\n第{slide.slide_number}页 ({slide.layout_type})")
        print(f"内容：")
        for key, value in slide.content.items():
            if isinstance(value, list):
                print(f"  {key}:")
                for item in value:
                    print(f"    - {item}")
            else:
                preview = str(value)[:60] + "..." if len(str(value)) > 60 else str(value)
                print(f"  {key}: {preview}")

    # Save outline to JSON
    output_dir = Path("examples/generated")
    ensure_dir(output_dir)

    outline_path = output_dir / "outline_annual_report.json"
    outline_dict = outline.model_dump(mode="json")
    # Convert datetime to string for JSON serialization
    outline_dict["metadata"]["generated_at"] = outline.metadata.generated_at.isoformat()

    save_json(outline_dict, outline_path)
    print(f"\n💾 大纲已保存到：{outline_path}")

    # Display JSON preview
    print("\n📄 JSON预览：")
    print("-" * 70)
    print(json.dumps(outline_dict, ensure_ascii=False, indent=2)[:500] + "...")

    print("\n" + "=" * 70)
    print("✨ 示例完成！")
    print("\n提示：这是使用Mock LLM的演示。")
    print("在.env中配置真实API密钥后，可以使用真实的LLM生成大纲。")
    print("=" * 70)


if __name__ == "__main__":
    main()
