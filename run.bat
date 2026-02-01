@echo off
REM PPT-Agent 快速运行脚本
REM Quick start script for PPT-Agent

echo.
echo ========================================================================
echo                    PPT-Agent 快速运行脚本
echo ========================================================================
echo.

REM 设置PYTHONPATH
set PYTHONPATH=%CD%

echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python未安装或不在PATH中
    pause
    exit /b 1
)
echo ✓ Python环境正常

echo.
echo [2/4] 检查依赖包...
python -c "import pptx, click, rich, pydantic, loguru" >nul 2>&1
if errorlevel 1 (
    echo ⚠ 缺少依赖包，正在安装...
    pip install -r requirements.txt
) else (
    echo ✓ 依赖包完整
)

echo.
echo [3/4] 可用的命令：
echo.
echo   1. 查看所有模板
echo   2. 生成PPT（使用Mock LLM演示）
echo   3. 运行测试
echo   4. 打开CLI帮助
echo   5. 退出
echo.

set /p choice="请选择操作 (1-5): "

if "%choice%"=="1" (
    echo.
    echo 提示：此命令需要配置API密钥，当前使用Mock模式
    echo.
    python -c "from src.template.loader import TemplateLoader; loader = TemplateLoader(); templates = loader.list_templates(); [print(f'• {t[\"template_id\"]}: {t[\"template_name\"]}') for t in templates]"
) else if "%choice%"=="2" (
    echo.
    echo 正在使用Mock LLM生成演示PPT...
    echo.
    python -c "import sys; sys.path.insert(0, '.'); exec(open('examples/full_ppt_generation.py').read())" 2>nul
    if errorlevel 1 (
        python examples\full_ppt_generation.py
    )
    echo.
    echo ✓ PPT已生成到 output/ 目录
    start output
) else if "%choice%"=="3" (
    echo.
    echo 运行测试套件...
    pytest tests/ -v
) else if "%choice%"=="4" (
    echo.
    python -m src.cli --help
) else if "%choice%"=="5" (
    echo.
    echo 再见！
    exit /b 0
) else (
    echo.
    echo ✗ 无效选择
)

echo.
echo [4/4] 完成！
echo.
echo 提示：配置API密钥后可使用完整功能
echo   编辑 .env 文件，添加：
echo   OPENAI_API_KEY=sk-your-key
echo   或 DEEPSEEK_API_KEY=sk-your-key
echo.
pause
