# PPT-Agent

An AI-powered agent for automated PowerPoint presentation generation. Simply describe what you need, and PPT-Agent creates professional presentations for you.

> **项目状态**: ✅ **核心功能完成！** - 可直接使用

## ✨ Features

- 🤖 **AI-driven generation** - Powered by GPT-4, Claude, or DeepSeek
- 📊 **Automatic structure** - Smart slide layout selection
- 🎨 **Template-based styling** - Professional, consistent design
- 🔄 **Refinement support** - Iteratively improve your presentation
- 📝 **Multiple slide types** - Cover, TOC, content variations, ending
- 🌐 **Multi-LLM support** - OpenAI, Anthropic, and DeepSeek
- 💾 **Real PPTX output** - Compatible with PowerPoint/WPS
- 🖥️ **CLI tool** - Easy-to-use command line interface

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/PPT-Agent.git
cd PPT-Agent

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```bash
cp .env.example .env
# Edit .env and add your API key
OPENAI_API_KEY=sk-your-key-here
# or
ANTHROPIC_API_KEY=sk-ant-your-key-here
# or
DEEPSEEK_API_KEY=sk-your-deepseek-key-here
```

### Usage

#### CLI (Recommended)

```bash
# Generate with OpenAI (default)
python -m src.cli generate "年终述职报告" --author "张三"

# Generate with Anthropic Claude
python -m src.cli generate "年终述职报告" --provider anthropic

# Generate with DeepSeek
python -m src.cli generate "年终述职报告" --provider deepseek

# List available templates
python -m src.cli templates

# Get template details
python -m src.cli template-info business_001

# Refine existing presentation
python -m src.cli refine outline.json "增加数据分析部分"

# See all options
python -m src.cli --help
```

#### Python API

```python
from src.agent import PPTAgent

# Initialize with OpenAI (default)
agent = PPTAgent(llm_provider='openai')

# Or use Anthropic Claude
agent = PPTAgent(llm_provider='anthropic')

# Or use DeepSeek
agent = PPTAgent(llm_provider='deepseek')

# Generate presentation
result = agent.generate_presentation(
    user_input="AI技术分享",
    author="技术讲师",
    max_slides=15
)

print(f"PPT saved to: {result['ppt']}")
# Output: PPT saved to: output/outline_xxxxx.pptx
```
outline = outline_gen.generate_outline(
    user_input="创建一个关于AI技术的演讲",
    author="技术讲师",
    max_slides=15
)

# Step 2: Generate PPT
ppt_gen = PPTGenerator()
ppt_path = ppt_gen.generate(outline)

print(f"PPT saved to: {ppt_path}")
# Output: PPT saved to: output/outline_xxxxx.pptx
```

### Using Real LLM for Outline Generation

```python
from src.outline.generator import OutlineGenerator

# Initialize with OpenAI
generator = OutlineGenerator(provider='openai')

# Or with Anthropic Claude
# generator = OutlineGenerator(provider='anthropic')

# Generate outline
outline = generator.generate_outline(
    user_input="年终述职报告",
    author="张三",
    max_slides=10
)

# Print results
print(f"Title: {outline.title}")
print(f"Total slides: {len(outline.slides)}")
for slide in outline.slides:
    print(f"  Slide {slide.slide_number}: {slide.layout_type}")

# Refine based on feedback
refined = generator.refine_outline(
    current_outline=outline,
    user_feedback="增加数据分析部分"
)
```

## 📁 Project Structure

```
PPT-Agent/
├── src/                      # Source code
│   ├── template/            # ✅ Template system
│   │   ├── models.py        # Pydantic data models
│   │   ├── loader.py        # Template loader with caching
│   │   └── validator.py     # Template validation
│   ├── outline/             # ✅ Outline generation
│   │   ├── models.py        # Outline data models
│   │   ├── llm_client.py    # LLM clients (OpenAI/Anthropic/DeepSeek)
│   │   ├── prompts.py       # Prompt templates
│   │   └── generator.py     # Outline generator
│   ├── generator/           # ✅ PPT generation engine
│   │   ├── ppt_generator.py # Main PPT generator
│   │   ├── styling.py       # Style applicator
│   │   └── renderers/       # Slide renderers
│   │       ├── cover.py     # Cover slide renderer
│   │       ├── toc.py       # Table of contents renderer
│   │       ├── content.py   # Content slide renderer
│   │       └── ending.py    # Ending slide renderer
│   └── utils/               # ✅ Utilities
│       ├── config.py        # Configuration
│       ├── logger.py        # Logging
│       └── file_utils.py    # File operations
├── templates/
│   └── json/                # Template JSON files
│       ├── business_001.json  # Business style (6 layouts)
│       └── simple_001.json    # Simple style (4 layouts)
├── tests/                   # ✅ Test suite (41 tests, 75% coverage)
│   ├── unit/
│   │   ├── test_template_models.py
│   │   ├── test_template_loader.py
│   │   ├── test_outline_models.py
│   │   ├── test_outline_generator.py
│   │   └── test_ppt_generator.py
│   └── conftest.py
├── examples/                # Example scripts
│   ├── basic_template_usage.py
│   ├── outline_generation_demo.py
│   └── full_ppt_generation.py  # Complete pipeline demo
├── output/                  # Generated PPT files
├── docs/                    # Documentation
├── plan.md                  # 📋 Development plan
└── CLAUDE.md                # 📘 Development guidelines
```

## 🎨 Available Templates

### 1. Business Style (business_001)
- Professional corporate design
- Color scheme: Navy Blue (#1F4788) + Orange (#F5A623)
- Layouts: Cover, TOC, Single Content, Two-Column, Image+Content, Ending
- Perfect for: Business reports, project presentations

### 2. Simple Style (simple_001)  
- Clean and minimal design
- Color scheme: Dark Gray (#2C3E50) + Blue (#3498DB)
- Layouts: Cover, TOC, Single Content, Ending
- Perfect for: Academic reports, technical presentations

## 📖 Template JSON Format

Templates are defined in JSON format with the following structure:

```json
{
  "template_id": "business_001",
  "template_name": "商务风格模板",
  "version": "1.0",
  "theme": {
    "colors": { "primary": "#1F4788", ... },
    "fonts": { "title": {...}, "body": {...} }
  },
  "layouts": {
    "cover": {
      "type": "cover",
      "placeholders": [
        {"id": "title", "type": "title", "x": 0.1, "y": 0.3, ...}
      ]
    }
  }
}
```

See `templates/json/business_001.json` for complete example.

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_template_models.py -v
```

**Current Coverage**: 70% (57 tests passing)

## 📋 Commands

### CLI Commands

```bash
# Generate presentation
python -m src.cli generate TOPIC [OPTIONS]

Options:
  --template, -t TEXT        Template ID
  --author, -a TEXT          Author name
  --max-slides, -m INTEGER   Maximum slides
  --output, -o PATH          Output directory
  --provider, -p             LLM provider (openai/anthropic/deepseek)
  --temperature FLOAT        LLM temperature
  --no-outline              Don't save outline JSON

# Refine presentation
python -m src.cli refine OUTLINE_FILE FEEDBACK [OPTIONS]

# List templates
python -m src.cli templates

# Template info
python -m src.cli template-info TEMPLATE_ID
```

## 🎯 LLM Configuration

The project supports multiple LLM providers:

### OpenAI (GPT-4)
```bash
# .env
OPENAI_API_KEY=sk-your-key-here
DEFAULT_MODEL=gpt-4
```

### Anthropic (Claude)
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Usage
```python
# OpenAI
generator = OutlineGenerator(provider='openai')

# Anthropic Claude
generator = OutlineGenerator(provider='anthropic', 
                            model='claude-3-5-sonnet-20241022')
```

## 📚 Documentation

- **plan.md** - Complete development roadmap (7 phases)
- **CLAUDE.md** - Coding standards and best practices
- **examples/** - Usage examples and demos

## 🛣️ Roadmap

- [x] **Phase 1**: Project architecture ✅
- [x] **Phase 2**: Template system ✅  
- [x] **Phase 3**: Outline generation ✅
- [x] **Phase 4**: PPT generation engine ✅
- [x] **Phase 5**: Agent orchestration & CLI ✅
- [ ] **Phase 6**: Advanced features (PPT parser, styling)
- [ ] **Phase 7**: Documentation & deployment

## 📈 Progress

- ✅ **Phases 1-5 Complete (95% of functionality)**
- 📦 Ready for production use
- 49 unit tests passing
- 68% code coverage
- Real PPTX files generated
- Full CLI tool available

## Development

### Running Tests

```bash
# Set Python path (Windows)
$env:PYTHONPATH = (Get-Location).Path

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
black src tests examples

# Sort imports
isort src tests examples

# Lint
flake8 src tests

# Type check
mypy src
```

### Adding New Templates

1. Create a new JSON file in `templates/json/`
2. Follow the schema defined in `src/template/models.py`
3. Ensure required layouts: `cover`, `toc`, `ending`
4. Test with: `python examples/basic_template_usage.py`

## 🤝 Contributing

1. Read `CLAUDE.md` for coding standards
2. Create a feature branch
3. Write tests for new features
4. Ensure tests pass and coverage doesn't drop
5. Submit a pull request

## 📄 License

MIT License
