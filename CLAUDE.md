# PPT-Agent 开发规范

> 本文档定义了PPT-Agent项目的代码规范、架构原则和最佳实践。所有开发者必须遵循此规范。

---

## 1. 代码风格规范

### 1.1 Python代码风格

**遵循标准**: PEP 8 + Google Python Style Guide

#### 命名规范
```python
# 模块名：小写下划线
# 文件名：template_parser.py, outline_generator.py

# 类名：大驼峰（PascalCase）
class PPTTemplateParser:
    pass

class OutlineGenerator:
    pass

# 函数名：小写下划线
def generate_outline(prompt: str) -> dict:
    pass

def parse_ppt_file(file_path: str) -> Template:
    pass

# 常量：大写下划线
MAX_SLIDES = 50
DEFAULT_FONT_SIZE = 18
TEMPLATE_DIR = "templates/"

# 私有变量/方法：前缀下划线
class Agent:
    def __init__(self):
        self._api_key = ""
    
    def _internal_method(self):
        pass
```

#### 类型注解（强制）
```python
from typing import List, Dict, Optional, Union
from pathlib import Path

def generate_slide(
    content: Dict[str, str],
    template: Template,
    slide_number: int
) -> Slide:
    """
    生成单个幻灯片
    
    Args:
        content: 幻灯片内容字典
        template: PPT模板对象
        slide_number: 幻灯片编号
    
    Returns:
        生成的幻灯片对象
    
    Raises:
        ValueError: 当内容格式不正确时
    """
    pass
```

#### 文档字符串（强制）
```python
def parse_template(file_path: Path) -> Dict[str, any]:
    """
    解析PPT模板文件为JSON格式
    
    将真实的PPTX文件解析为标准化的模板JSON结构，提取版式、
    颜色方案、字体配置等信息。
    
    Args:
        file_path: PPT模板文件的路径
    
    Returns:
        包含模板配置的字典，格式如下:
        {
            "template_id": str,
            "theme": {...},
            "layouts": {...}
        }
    
    Raises:
        FileNotFoundError: 模板文件不存在
        InvalidTemplateError: 模板格式无效
    
    Example:
        >>> template = parse_template(Path("templates/business.pptx"))
        >>> print(template["template_id"])
        "business_001"
    """
    pass
```

### 1.2 代码格式化工具

**必须使用**:
- **Black**: 自动代码格式化（行长度88）
- **isort**: 导入语句排序
- **flake8**: 代码检查
- **mypy**: 类型检查

**配置文件** (`pyproject.toml`):
```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**Git Hook**: 提交前自动格式化
```bash
# .git/hooks/pre-commit
#!/bin/bash
black .
isort .
flake8 src tests
mypy src
```

---

## 2. 项目架构规范

### 2.1 目录结构

```
PPT-Agent/
├── src/                          # 源代码
│   ├── __init__.py
│   ├── agent/                    # Agent编排层
│   │   ├── __init__.py
│   │   ├── ppt_agent.py         # 主Agent类
│   │   └── workflow.py          # 工作流编排
│   ├── template/                 # 模板系统
│   │   ├── __init__.py
│   │   ├── models.py            # 模板数据模型（Pydantic）
│   │   ├── parser.py            # PPT解析器
│   │   ├── loader.py            # 模板加载器
│   │   └── validator.py         # 模板验证器
│   ├── outline/                  # 大纲生成模块
│   │   ├── __init__.py
│   │   ├── generator.py         # 大纲生成器
│   │   ├── prompts.py           # LLM提示词
│   │   ├── models.py            # 大纲数据模型
│   │   └── llm_client.py        # LLM客户端
│   ├── generator/                # PPT生成引擎
│   │   ├── __init__.py
│   │   ├── ppt_generator.py     # 主生成器
│   │   ├── slide_factory.py     # 幻灯片工厂
│   │   ├── renderers/           # 渲染器
│   │   │   ├── cover.py
│   │   │   ├── toc.py
│   │   │   ├── content.py
│   │   │   └── ending.py
│   │   └── styling.py           # 样式应用
│   ├── utils/                    # 工具函数
│   │   ├── __init__.py
│   │   ├── file_utils.py
│   │   ├── logger.py
│   │   └── config.py
│   └── exceptions.py             # 自定义异常
│
├── tests/                        # 测试代码
│   ├── unit/                     # 单元测试
│   ├── integration/              # 集成测试
│   ├── fixtures/                 # 测试数据
│   └── conftest.py
│
├── templates/                    # PPT模板文件
│   ├── json/                     # 模板JSON
│   │   ├── business_001.json
│   │   ├── simple_001.json
│   │   └── academic_001.json
│   └── pptx/                     # 原始PPTX（参考）
│       └── business.pptx
│
├── examples/                     # 示例和Demo
│   ├── basic_usage.py
│   ├── custom_template.py
│   └── generated/                # 生成示例输出
│
├── docs/                         # 文档
│   ├── api.md                    # API文档
│   ├── template_guide.md         # 模板开发指南
│   └── user_guide.md             # 用户指南
│
├── .env.example                  # 环境变量示例
├── .gitignore
├── pyproject.toml                # 项目配置
├── requirements.txt              # 依赖列表
├── requirements-dev.txt          # 开发依赖
├── README.md
├── plan.md                       # 开发计划
└── CLAUDE.md                     # 本文档
```

### 2.2 分层架构

```
┌─────────────────────────────────────┐
│         用户接口层 (CLI/API)         │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│         Agent编排层 (Workflow)       │  ← 流程控制、状态管理
└─────────────────────────────────────┘
                  ↓
        ┌─────────┴─────────┐
        ↓                   ↓
┌─────────────────┐  ┌─────────────────┐
│   大纲生成模块   │  │   模板系统      │  ← 业务逻辑层
│   (LLM调用)     │  │  (加载/解析)    │
└─────────────────┘  └─────────────────┘
                  ↓
┌─────────────────────────────────────┐
│         PPT生成引擎                  │  ← 核心生成逻辑
│  (Slide Factory + Renderers)       │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│      python-pptx 底层库              │  ← 基础设施层
└─────────────────────────────────────┘
```

**设计原则**:
- **单一职责**: 每个模块只负责一个明确的功能
- **依赖倒置**: 高层模块不依赖低层实现细节
- **开闭原则**: 对扩展开放，对修改封闭（如新增模板类型）

---

## 3. 数据模型规范

### 3.1 使用Pydantic进行数据验证

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum

class LayoutType(str, Enum):
    """幻灯片布局类型"""
    COVER = "cover"
    TOC = "table_of_contents"
    CONTENT_SINGLE = "content_single"
    CONTENT_TWO_COLUMN = "content_two_column"
    ENDING = "ending"

class Placeholder(BaseModel):
    """占位符定义"""
    id: str = Field(..., description="占位符唯一标识")
    type: str = Field(..., description="占位符类型：text/image/chart")
    x: float = Field(..., ge=0, le=1, description="X坐标（相对位置0-1）")
    y: float = Field(..., ge=0, le=1, description="Y坐标（相对位置0-1）")
    width: float = Field(..., ge=0, le=1, description="宽度（相对值）")
    height: float = Field(..., ge=0, le=1, description="高度（相对值）")
    
    @validator('width', 'height')
    def check_size(cls, v):
        if v <= 0:
            raise ValueError("宽度和高度必须大于0")
        return v

class Layout(BaseModel):
    """布局定义"""
    type: LayoutType
    placeholders: List[Placeholder]
    background: Optional[dict] = None

class Template(BaseModel):
    """PPT模板"""
    template_id: str = Field(..., regex=r'^[a-z_]+_\d{3}$')
    template_name: str
    version: str = "1.0"
    theme: dict
    layouts: Dict[str, Layout]
    
    class Config:
        json_schema_extra = {
            "example": {
                "template_id": "business_001",
                "template_name": "商务风格模板",
                "version": "1.0",
                "theme": {...},
                "layouts": {...}
            }
        }
```

### 3.2 JSON Schema验证

所有JSON文件（模板、大纲）必须有对应的Schema定义，存放在 `src/schemas/` 目录。

---

## 4. 错误处理规范

### 4.1 自定义异常

```python
# src/exceptions.py

class PPTAgentException(Exception):
    """基础异常类"""
    pass

class TemplateError(PPTAgentException):
    """模板相关错误"""
    pass

class TemplateNotFoundError(TemplateError):
    """模板未找到"""
    pass

class InvalidTemplateError(TemplateError):
    """模板格式无效"""
    pass

class OutlineGenerationError(PPTAgentException):
    """大纲生成错误"""
    pass

class LLMAPIError(OutlineGenerationError):
    """LLM API调用失败"""
    pass

class PPTGenerationError(PPTAgentException):
    """PPT生成错误"""
    pass
```

### 4.2 错误处理模式

```python
from loguru import logger
from typing import Optional

def safe_generate_outline(prompt: str, retries: int = 3) -> Optional[dict]:
    """
    安全的大纲生成，带重试机制
    """
    for attempt in range(retries):
        try:
            outline = llm_client.generate(prompt)
            validate_outline(outline)
            return outline
        except LLMAPIError as e:
            logger.warning(f"LLM调用失败 (尝试 {attempt + 1}/{retries}): {e}")
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)  # 指数退避
        except ValidationError as e:
            logger.error(f"大纲验证失败: {e}")
            raise OutlineGenerationError(f"生成的大纲格式不正确: {e}")
    
    return None
```

---

## 5. 日志规范

### 5.1 使用loguru

```python
from loguru import logger
import sys

# 配置日志
logger.remove()  # 移除默认handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/ppt_agent_{time:YYYY-MM-DD}.log",
    rotation="00:00",  # 每天轮转
    retention="30 days",
    level="DEBUG"
)

# 使用示例
logger.info("开始生成PPT大纲")
logger.debug(f"使用模板: {template_id}")
logger.warning("API响应时间超过5秒")
logger.error("模板文件损坏", exc_info=True)
```

### 5.2 日志级别使用

- **DEBUG**: 详细的调试信息（参数值、中间状态）
- **INFO**: 关键流程节点（开始生成、完成生成）
- **WARNING**: 可恢复的异常（API重试、降级处理）
- **ERROR**: 严重错误（文件损坏、生成失败）
- **CRITICAL**: 系统级错误（配置缺失、依赖缺失）

---

## 6. 测试规范

### 6.1 测试覆盖率要求

- **最低覆盖率**: 80%
- **核心模块覆盖率**: 90%+（template, outline, generator）

### 6.2 测试结构

```python
# tests/unit/test_template_parser.py

import pytest
from pathlib import Path
from src.template.parser import TemplateParser
from src.exceptions import InvalidTemplateError

class TestTemplateParser:
    """模板解析器测试"""
    
    @pytest.fixture
    def sample_pptx(self):
        """测试用PPT文件"""
        return Path("tests/fixtures/sample.pptx")
    
    def test_parse_valid_template(self, sample_pptx):
        """测试解析有效模板"""
        parser = TemplateParser()
        result = parser.parse(sample_pptx)
        
        assert result["template_id"] is not None
        assert "layouts" in result
        assert len(result["layouts"]) > 0
    
    def test_parse_invalid_file(self):
        """测试解析无效文件"""
        parser = TemplateParser()
        
        with pytest.raises(FileNotFoundError):
            parser.parse(Path("nonexistent.pptx"))
    
    def test_parse_corrupted_pptx(self, corrupted_pptx):
        """测试解析损坏的PPT"""
        parser = TemplateParser()
        
        with pytest.raises(InvalidTemplateError):
            parser.parse(corrupted_pptx)
    
    @pytest.mark.parametrize("layout_type,expected_placeholders", [
        ("cover", 3),
        ("toc", 2),
        ("content_single", 2)
    ])
    def test_layout_placeholders(self, sample_pptx, layout_type, expected_placeholders):
        """测试不同布局的占位符数量"""
        parser = TemplateParser()
        result = parser.parse(sample_pptx)
        
        assert len(result["layouts"][layout_type]["placeholders"]) == expected_placeholders
```

### 6.3 Mock和Fixture

```python
# tests/conftest.py

import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_llm_client():
    """模拟LLM客户端"""
    client = Mock()
    client.generate.return_value = {
        "title": "测试PPT",
        "slides": [...]
    }
    return client

@pytest.fixture
def sample_outline():
    """示例大纲数据"""
    return {
        "outline_id": "test_001",
        "title": "测试PPT",
        "slides": [
            {"slide_number": 1, "layout_type": "cover", ...}
        ]
    }
```

---

## 7. 配置管理规范

### 7.1 使用.env文件

```bash
# .env
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
DEFAULT_MODEL=gpt-4
TEMPLATE_DIR=templates/json
OUTPUT_DIR=output
MAX_SLIDES=50
TEMPERATURE=0.7
LOG_LEVEL=INFO
```

### 7.2 配置加载

```python
# src/utils/config.py

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置"""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_model: str = "gpt-4"
    template_dir: str = "templates/json"
    output_dir: str = "output"
    max_slides: int = 50
    temperature: float = 0.7
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 全局配置实例
settings = Settings()
```

---

## 8. Git规范

### 8.1 分支策略

- **main**: 稳定发布分支
- **dev**: 开发主分支
- **feature/xxx**: 功能分支
- **fix/xxx**: 修复分支
- **hotfix/xxx**: 紧急修复

### 8.2 Commit Message规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型**:
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具链

**示例**:
```
feat(template): 添加PPT模板解析功能

- 实现TemplateParser类
- 支持解析版式和颜色方案
- 添加单元测试

Closes #12
```

---

## 9. 性能规范

### 9.1 性能目标

- 大纲生成: < 30秒
- PPT生成: < 90秒（10页）
- 模板加载: < 1秒
- 内存占用: < 500MB

### 9.2 优化原则

```python
# ❌ 避免：重复读取文件
for slide in slides:
    template = load_template(template_path)  # 每次都加载
    generate_slide(slide, template)

# ✅ 推荐：缓存模板
template = load_template(template_path)  # 只加载一次
for slide in slides:
    generate_slide(slide, template)

# ✅ 使用functools.lru_cache
from functools import lru_cache

@lru_cache(maxsize=10)
def load_template(template_id: str) -> Template:
    """缓存已加载的模板"""
    pass
```

---

## 10. 文档规范

### 10.1 README必须包含

- 项目简介和特性
- 快速开始（安装、配置、使用）
- 示例代码
- 项目结构
- 开发指南
- 许可证

### 10.2 代码内文档

- 每个模块：模块级文档字符串
- 每个类：类文档字符串 + 属性说明
- 每个公开函数：完整的文档字符串（Args、Returns、Raises、Example）
- 复杂逻辑：行内注释

---

## 11. 依赖管理

### 11.1 版本锁定

```txt
# requirements.txt
python-pptx==0.6.23
openai==1.12.0
anthropic==0.18.1
pydantic==2.6.1
loguru==0.7.2
```

### 11.2 定期更新

- 每月检查依赖更新
- 使用 `pip list --outdated` 检查过期包
- 更新前在dev分支测试

---

## 12. 安全规范

### 12.1 敏感信息

- **禁止**: 硬编码API密钥
- **禁止**: 提交.env文件到Git
- **必须**: 使用环境变量
- **必须**: 在.gitignore中排除敏感文件

### 12.2 输入验证

```python
# ✅ 验证用户输入
def generate_presentation(prompt: str, max_slides: int = 10) -> str:
    if not prompt or len(prompt) < 5:
        raise ValueError("提示词至少需要5个字符")
    
    if max_slides < 1 or max_slides > 100:
        raise ValueError("幻灯片数量必须在1-100之间")
    
    # 清理输入，防止注入攻击
    prompt = prompt.strip()
    
    # ...
```

---

## 13. Code Review检查清单

提交PR前自检：

- [ ] 代码通过所有测试（pytest）
- [ ] 代码覆盖率不低于现有水平
- [ ] 通过Black、isort格式化
- [ ] 通过flake8和mypy检查
- [ ] 添加了必要的文档字符串
- [ ] 更新了相关文档（如README）
- [ ] Commit message符合规范
- [ ] 没有遗留的print()或调试代码
- [ ] 敏感信息已移除
- [ ] 新功能有对应的测试用例

---

## 14. 开发环境设置

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. 安装pre-commit hooks
pre-commit install

# 4. 配置.env
cp .env.example .env
# 编辑.env，填入API密钥

# 5. 运行测试验证环境
pytest tests/ -v
```

---

## 15. 持续集成（CI）

### GitHub Actions配置

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: flake8 src tests
    
    - name: Type check with mypy
      run: mypy src
    
    - name: Test with pytest
      run: pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## 附录：常用命令

```bash
# 格式化代码
black .
isort .

# 代码检查
flake8 src tests
mypy src

# 运行测试
pytest                          # 所有测试
pytest tests/unit              # 单元测试
pytest -v                      # 详细输出
pytest --cov=src              # 覆盖率报告
pytest -k "test_template"     # 运行特定测试

# 依赖管理
pip install -r requirements.txt
pip freeze > requirements.txt
pip list --outdated

# 生成文档
pdoc --html --output-dir docs src
```

---

**文档版本**: v1.0  
**最后更新**: 2024-01-15  
**维护者**: PPT-Agent开发团队
