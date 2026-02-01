"""
Example: Basic template usage
"""

from pathlib import Path
from src.template.loader import TemplateLoader
from src.template.validator import TemplateValidator


def main():
    """Demonstrate basic template loading and validation"""

    # Initialize loader
    loader = TemplateLoader()

    # List all available templates
    print("=" * 60)
    print("Available Templates:")
    print("=" * 60)
    templates = loader.list_templates()
    for i, template_info in enumerate(templates, 1):
        print(f"\n{i}. {template_info['template_name']}")
        print(f"   ID: {template_info['template_id']}")
        print(f"   Version: {template_info['version']}")
        print(f"   Description: {template_info.get('description', 'N/A')}")

    # Load and validate a template
    print("\n" + "=" * 60)
    print("Loading and Validating Template: business_001")
    print("=" * 60)

    template = loader.load_template("business_001")

    print(f"\nTemplate Name: {template.template_name}")
    print(f"Template ID: {template.template_id}")
    print(f"Version: {template.version}")

    # Show theme colors
    print("\nTheme Colors:")
    print(f"  Primary: {template.theme.colors.primary}")
    print(f"  Secondary: {template.theme.colors.secondary}")
    print(f"  Accent: {template.theme.colors.accent}")

    # Show available layouts
    print("\nAvailable Layouts:")
    for layout_name, layout in template.layouts.items():
        print(f"  - {layout_name} ({layout.type.value})")
        print(f"    Placeholders: {len(layout.placeholders)}")
        for ph in layout.placeholders:
            print(f"      • {ph.id} ({ph.type.value})")

    # Validate template
    validator = TemplateValidator()
    try:
        validator.validate_template(template)
        print("\n✅ Template validation: PASSED")
    except ValueError as e:
        print(f"\n❌ Template validation: FAILED - {e}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
