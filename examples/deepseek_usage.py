"""
Example: Using DeepSeek model for PPT generation
"""

from pathlib import Path
from src.agent import PPTAgent
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Generate PPT using DeepSeek model"""
    
    print("="*70)
    print("DeepSeek PPT Generation Example")
    print("="*70)
    
    # Initialize agent with DeepSeek
    # Note: Make sure DEEPSEEK_API_KEY is set in .env file
    try:
        agent = PPTAgent(llm_provider='deepseek')
        print("\n✓ DeepSeek agent initialized")
    except ValueError as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease set DEEPSEEK_API_KEY in your .env file:")
        print("  DEEPSEEK_API_KEY=sk-your-deepseek-key-here")
        return
    
    # Example 1: Generate a presentation
    print("\n" + "-"*70)
    print("Example 1: Generate AI presentation with DeepSeek")
    print("-"*70)
    
    try:
        result = agent.generate_presentation(
            user_input="人工智能技术分享：从基础到应用",
            author="DeepSeek演示",
            template_id="business_001",
            max_slides=12,
            output_dir=Path("examples/generated"),
        )
        
        print(f"\n✓ PPT generated: {result['ppt']}")
        print(f"✓ Outline saved: {result['outline']}")
        print(f"✓ File size: {result['ppt'].stat().st_size / 1024:.1f} KB")
        
    except Exception as e:
        print(f"\n✗ Generation failed: {e}")
        logger.error(f"DeepSeek generation error: {e}")
    
    # Example 2: List available templates
    print("\n" + "-"*70)
    print("Example 2: Available templates")
    print("-"*70)
    
    templates = agent.list_templates()
    for template in templates:
        print(f"\n• {template['template_id']}")
        print(f"  名称: {template['template_name']}")
        print(f"  版本: {template['version']}")
    
    # Example 3: DeepSeek advantages
    print("\n" + "-"*70)
    print("DeepSeek Advantages")
    print("-"*70)
    print("""
✓ Cost-effective: Lower API pricing compared to GPT-4
✓ Fast response: Optimized for Chinese language tasks
✓ Good quality: Comparable performance for structured tasks
✓ OpenAI-compatible: Easy integration with existing code
✓ Domestic access: Better network connectivity in China
    """)
    
    print("\n" + "="*70)
    print("DeepSeek example completed!")
    print("="*70)


if __name__ == "__main__":
    main()
