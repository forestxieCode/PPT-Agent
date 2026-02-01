"""
CLI - Command Line Interface for PPT-Agent
"""

import sys
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich import print as rprint

from src.agent.ppt_agent import PPTAgent
from src.utils.config import settings
from src.utils.logger import get_logger
from src.exceptions import PPTAgentException

console = Console()
logger = get_logger(__name__)


@click.group()
@click.version_option(version="0.1.0", prog_name="PPT-Agent")
def cli():
    """
    🎨 PPT-Agent - AI-powered PowerPoint generation
    
    Generate professional presentations with AI assistance.
    """
    pass


@cli.command()
@click.argument("topic")
@click.option(
    "--template",
    "-t",
    help="Template ID to use (default: auto-select)",
    default=None,
)
@click.option("--author", "-a", help="Author name", default=None)
@click.option(
    "--max-slides",
    "-m",
    help="Maximum number of slides",
    type=int,
    default=None,
)
@click.option(
    "--output",
    "-o",
    help="Output directory",
    type=click.Path(path_type=Path),
    default=None,
)
@click.option(
    "--provider",
    "-p",
    help="LLM provider (openai or anthropic)",
    type=click.Choice(["openai", "anthropic"]),
    default="openai",
)
@click.option(
    "--temperature",
    help="LLM temperature (0.0-2.0)",
    type=float,
    default=None,
)
@click.option(
    "--no-outline",
    is_flag=True,
    help="Don't save outline JSON",
    default=False,
)
def generate(
    topic, template, author, max_slides, output, provider, temperature, no_outline
):
    """
    Generate a new PPT presentation
    
    TOPIC: Presentation topic or requirements
    
    Examples:
    
      ppt-agent generate "年终述职报告" --author "张三"
      
      ppt-agent generate "Python教程" --template simple_001 --max-slides 15
      
      ppt-agent generate "产品发布会" --provider anthropic
    """
    try:
        # Display header
        console.print(
            Panel.fit(
                "[bold cyan]🎨 PPT-Agent[/bold cyan]\n"
                "[dim]AI-powered PowerPoint generation[/dim]",
                border_style="cyan",
            )
        )

        # Display configuration
        console.print("\n[bold]Configuration:[/bold]")
        config_table = Table(show_header=False, box=None)
        config_table.add_column("Key", style="cyan")
        config_table.add_column("Value", style="white")
        config_table.add_row("Topic", topic)
        config_table.add_row("LLM Provider", provider)
        if template:
            config_table.add_row("Template", template)
        if author:
            config_table.add_row("Author", author)
        if max_slides:
            config_table.add_row("Max Slides", str(max_slides))
        console.print(config_table)
        console.print()

        # Initialize agent
        agent = PPTAgent(llm_provider=provider)

        # Generate presentation with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Generating presentation...", total=3)

            # Step 1: Generate outline
            progress.update(task, description="[cyan]Step 1/3: Generating outline...")
            
            try:
                result = agent.generate_presentation(
                    user_input=topic,
                    template_id=template,
                    author=author,
                    max_slides=max_slides,
                    output_dir=output,
                    save_outline=not no_outline,
                    temperature=temperature,
                )
                progress.advance(task)

                # Step 2 & 3 are handled internally
                progress.update(task, description="[cyan]Step 2/3: Validating template...")
                progress.advance(task)
                
                progress.update(task, description="[cyan]Step 3/3: Generating PPT...")
                progress.advance(task)

            except Exception as e:
                progress.stop()
                console.print(f"\n[bold red]❌ Error:[/bold red] {e}")
                logger.error(f"Generation failed: {e}")
                sys.exit(1)

        # Display success
        console.print("\n[bold green]✅ Success![/bold green]")
        
        result_table = Table(show_header=False, box=None)
        result_table.add_column("File", style="cyan")
        result_table.add_column("Path", style="white")
        result_table.add_row("PPT", str(result["ppt"]))
        if "outline" in result:
            result_table.add_row("Outline", str(result["outline"]))
        console.print(result_table)

        ppt_size = result["ppt"].stat().st_size / 1024
        console.print(f"\n[dim]File size: {ppt_size:.1f} KB[/dim]")
        
        console.print("\n[bold cyan]💡 Next steps:[/bold cyan]")
        console.print("  • Open the PPT file with PowerPoint or WPS")
        console.print("  • Use 'ppt-agent refine' to modify the presentation")

    except PPTAgentException as e:
        console.print(f"\n[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("outline_file", type=click.Path(exists=True, path_type=Path))
@click.argument("feedback")
@click.option(
    "--output",
    "-o",
    help="Output directory",
    type=click.Path(path_type=Path),
    default=None,
)
@click.option(
    "--provider",
    "-p",
    help="LLM provider",
    type=click.Choice(["openai", "anthropic"]),
    default="openai",
)
def refine(outline_file, feedback, output, provider):
    """
    Refine an existing presentation
    
    OUTLINE_FILE: Path to outline JSON file
    FEEDBACK: Modification request
    
    Examples:
    
      ppt-agent refine outline.json "增加数据分析部分"
      
      ppt-agent refine outline.json "使用更简洁的语言"
    """
    try:
        console.print(
            Panel.fit(
                "[bold cyan]🔄 Refining Presentation[/bold cyan]",
                border_style="cyan",
            )
        )

        console.print(f"\n[bold]Outline:[/bold] {outline_file}")
        console.print(f"[bold]Feedback:[/bold] {feedback}\n")

        agent = PPTAgent(llm_provider=provider)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Refining presentation...", total=None)

            result = agent.refine_presentation(
                outline_path=outline_file,
                user_feedback=feedback,
                output_dir=output,
            )

        console.print("\n[bold green]✅ Presentation refined![/bold green]")
        console.print(f"\nNew PPT: [cyan]{result['ppt']}[/cyan]")
        console.print(f"New Outline: [cyan]{result['outline']}[/cyan]")

    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
def templates():
    """
    List all available templates
    
    Example:
    
      ppt-agent templates
    """
    try:
        agent = PPTAgent()
        template_list = agent.list_templates()

        console.print(
            Panel.fit(
                "[bold cyan]📋 Available Templates[/bold cyan]",
                border_style="cyan",
            )
        )
        console.print()

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("ID", style="yellow")
        table.add_column("Name", style="white")
        table.add_column("Version", style="dim")
        table.add_column("Description", style="dim")

        for template in template_list:
            table.add_row(
                template["template_id"],
                template["template_name"],
                template["version"],
                template.get("description", ""),
            )

        console.print(table)
        console.print(f"\n[dim]Total: {len(template_list)} templates[/dim]")

    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("template_id")
def template_info(template_id):
    """
    Show detailed information about a template
    
    TEMPLATE_ID: Template identifier
    
    Example:
    
      ppt-agent template-info business_001
    """
    try:
        agent = PPTAgent()
        info = agent.get_template_info(template_id)

        console.print(
            Panel.fit(
                f"[bold cyan]Template: {info['template_name']}[/bold cyan]",
                border_style="cyan",
            )
        )
        console.print()

        info_table = Table(show_header=False, box=None)
        info_table.add_column("Key", style="cyan")
        info_table.add_column("Value", style="white")
        
        info_table.add_row("ID", info["template_id"])
        info_table.add_row("Name", info["template_name"])
        info_table.add_row("Version", info["version"])
        if info.get("description"):
            info_table.add_row("Description", info["description"])

        console.print(info_table)

    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()
