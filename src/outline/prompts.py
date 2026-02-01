"""
Prompt templates for outline generation
"""

from typing import Dict, List, Optional


class PromptTemplate:
    """Prompt template manager"""

    # System prompt for outline generation
    SYSTEM_PROMPT = """你是一个专业的PPT大纲生成助手。根据用户提供的主题，生成结构化的PPT大纲。

要求：
1. 生成的大纲必须包含封面页、目录页、内容页和结束页
2. 内容页数量根据主题复杂度合理安排（建议5-15页）
3. 每页内容要充实、有条理，避免空洞
4. 使用清晰的标题和要点
5. 返回格式必须是有效的JSON

输出JSON格式：
{
  "title": "PPT标题",
  "author": "作者名称（如果未指定可留空）",
  "template_id": "推荐的模板ID（business_001或simple_001）",
  "slides": [
    {
      "slide_number": 1,
      "layout_type": "cover",
      "content": {
        "title": "演示标题",
        "subtitle": "副标题",
        "author": "作者",
        "date": "日期"
      },
      "notes": "演讲备注（可选）"
    },
    {
      "slide_number": 2,
      "layout_type": "toc",
      "content": {
        "title": "目录",
        "items": ["第一部分", "第二部分", "第三部分"]
      }
    },
    {
      "slide_number": 3,
      "layout_type": "content_single",
      "content": {
        "title": "章节标题",
        "content": "详细内容，可以使用\\n换行"
      }
    },
    {
      "slide_number": N,
      "layout_type": "ending",
      "content": {
        "message": "感谢聆听！",
        "contact": "联系方式（可选）"
      }
    }
  ]
}

可用的布局类型（layout_type）：
- cover: 封面页（必须是第1页）
- toc 或 table_of_contents: 目录页（必须有）
- content_single: 单栏内容页
- content_two_column: 双栏内容页
- content_image: 图文混排页
- ending: 结束页（必须是最后1页）"""

    # Example prompts for different scenarios
    EXAMPLES = {
        "年终述职": {
            "prompt": "生成一个年终述职报告的PPT大纲",
            "expected_sections": [
                "工作回顾",
                "核心成果",
                "数据展示",
                "遇到的挑战",
                "经验总结",
                "下一年计划",
            ],
        },
        "产品发布": {
            "prompt": "生成一个新产品发布的PPT大纲",
            "expected_sections": [
                "市场背景",
                "产品介绍",
                "核心功能",
                "技术优势",
                "应用场景",
                "定价策略",
            ],
        },
        "技术分享": {
            "prompt": "生成一个技术分享的PPT大纲，主题是Python异步编程",
            "expected_sections": [
                "异步编程概述",
                "async/await语法",
                "实战案例",
                "性能对比",
                "最佳实践",
            ],
        },
    }

    @staticmethod
    def create_outline_prompt(
        user_input: str,
        template_id: Optional[str] = None,
        max_slides: int = 15,
        author: Optional[str] = None,
    ) -> str:
        """
        Create outline generation prompt

        Args:
            user_input: User's presentation topic/requirements
            template_id: Specific template to use (optional)
            max_slides: Maximum number of slides
            author: Author name (optional)

        Returns:
            Formatted prompt string
        """
        prompt_parts = [f"请根据以下需求生成PPT大纲：\n\n主题：{user_input}\n"]

        if template_id:
            prompt_parts.append(f"指定模板：{template_id}\n")

        if author:
            prompt_parts.append(f"作者：{author}\n")

        prompt_parts.append(f"\n要求：")
        prompt_parts.append(f"- 总页数控制在{max_slides}页以内")
        prompt_parts.append(f"- 第1页必须是封面页（cover）")
        prompt_parts.append(f"- 第2页必须是目录页（toc）")
        prompt_parts.append(f"- 最后1页必须是结束页（ending）")
        prompt_parts.append(f"- 内容页要详实，避免过于简单")
        prompt_parts.append(f"- 返回完整的JSON格式")

        if not template_id:
            prompt_parts.append(
                f"\n根据主题推荐合适的模板："
                f"\n- business_001: 商务风格，适合企业汇报、项目展示"
                f"\n- simple_001: 简约风格，适合学术报告、技术分享"
            )

        return "\n".join(prompt_parts)

    @staticmethod
    def create_refinement_prompt(
        current_outline: Dict,
        user_feedback: str,
    ) -> str:
        """
        Create prompt for outline refinement

        Args:
            current_outline: Current outline JSON
            user_feedback: User's feedback/modification request

        Returns:
            Refinement prompt
        """
        import json

        prompt = f"""当前PPT大纲：
```json
{json.dumps(current_outline, ensure_ascii=False, indent=2)}
```

用户反馈：
{user_feedback}

请根据用户反馈修改大纲，保持JSON格式不变。"""

        return prompt

    @staticmethod
    def create_expansion_prompt(
        slide_content: Dict,
        slide_number: int,
    ) -> str:
        """
        Create prompt to expand a specific slide

        Args:
            slide_content: Current slide content
            slide_number: Slide number to expand

        Returns:
            Expansion prompt
        """
        import json

        prompt = f"""请扩展第{slide_number}页的内容，使其更加详细和充实。

当前内容：
```json
{json.dumps(slide_content, ensure_ascii=False, indent=2)}
```

要求：
- 保持JSON格式
- 增加更多细节和要点
- 使内容更加丰富和专业"""

        return prompt

    @staticmethod
    def get_few_shot_examples() -> List[Dict[str, str]]:
        """
        Get few-shot learning examples

        Returns:
            List of example prompts and expected outputs
        """
        return [
            {
                "prompt": "生成一个5页的产品介绍PPT大纲，产品是AI写作助手",
                "output": """{
  "title": "AI写作助手产品介绍",
  "author": "",
  "template_id": "business_001",
  "slides": [
    {
      "slide_number": 1,
      "layout_type": "cover",
      "content": {
        "title": "AI写作助手产品介绍",
        "subtitle": "让写作更高效、更智能",
        "author": "产品团队",
        "date": "2024年1月"
      }
    },
    {
      "slide_number": 2,
      "layout_type": "toc",
      "content": {
        "title": "目录",
        "items": ["产品概述", "核心功能", "应用场景"]
      }
    },
    {
      "slide_number": 3,
      "layout_type": "content_single",
      "content": {
        "title": "产品概述",
        "content": "AI写作助手是一款基于大语言模型的智能写作工具\\n\\n• 支持多种写作场景\\n• 提供实时写作建议\\n• 智能改写和润色\\n• 多语言支持"
      }
    },
    {
      "slide_number": 4,
      "layout_type": "content_two_column",
      "content": {
        "title": "核心功能",
        "content_left": "智能续写\\n• 根据上下文自动续写\\n• 多种风格选择\\n• 实时预览",
        "content_right": "内容优化\\n• 语法纠错\\n• 用词优化\\n• 格式调整"
      }
    },
    {
      "slide_number": 5,
      "layout_type": "ending",
      "content": {
        "message": "感谢观看！",
        "contact": "联系我们：ai-writer@example.com"
      }
    }
  ]
}""",
            }
        ]
