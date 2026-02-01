"""
Main PPT Agent - Orchestrates the complete workflow
"""

from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from src.outline.generator import OutlineGenerator
from src.outline.models import Outline
from src.generator.ppt_generator import PPTGenerator
from src.template.loader import TemplateLoader
from src.utils.logger import get_logger
from src.utils.config import settings
from src.utils.file_utils import save_json, ensure_dir
from src.exceptions import PPTAgentException

logger = get_logger(__name__)


class PPTAgent:
    """
    Main PPT Agent - One-stop solution for PPT generation
    
    Orchestrates the complete workflow:
    1. Template selection
    2. Outline generation (LLM)
    3. PPT generation
    4. Output management
    """

    def __init__(
        self,
        llm_provider: str = "openai",
        template_loader: Optional[TemplateLoader] = None,
    ):
        """
        Initialize PPT Agent

        Args:
            llm_provider: LLM provider ("openai" or "anthropic")
            template_loader: Template loader instance (optional)
        """
        self.llm_provider = llm_provider
        self.template_loader = template_loader or TemplateLoader()
        
        # Initialize components
        self.outline_generator = OutlineGenerator(provider=llm_provider)
        self.ppt_generator = PPTGenerator(template_loader=self.template_loader)
        
        logger.info(f"Initialized PPTAgent with LLM provider: {llm_provider}")

    def generate_presentation(
        self,
        user_input: str,
        template_id: Optional[str] = None,
        author: Optional[str] = None,
        max_slides: Optional[int] = None,
        output_dir: Optional[Path] = None,
        save_outline: bool = True,
        temperature: Optional[float] = None,
    ) -> Dict[str, Path]:
        """
        Generate complete PPT presentation from user input
        
        This is the main entry point for PPT generation. It handles:
        - Template selection (auto or manual)
        - Outline generation using LLM
        - PPT file generation
        - File management
        
        Args:
            user_input: User's presentation topic/requirements
            template_id: Specific template ID to use (optional, auto-select if not provided)
            author: Author name (optional)
            max_slides: Maximum number of slides (optional, uses settings default)
            output_dir: Output directory (optional, uses settings default)
            save_outline: Whether to save outline JSON (default: True)
            temperature: LLM temperature (optional, uses settings default)
        
        Returns:
            Dictionary with paths to generated files:
            {
                "ppt": Path to PPT file,
                "outline": Path to outline JSON (if save_outline=True)
            }
        
        Raises:
            PPTAgentException: Failed to generate presentation
        
        Example:
            >>> agent = PPTAgent(llm_provider="openai")
            >>> result = agent.generate_presentation(
            ...     user_input="年终述职报告",
            ...     author="张三"
            ... )
            >>> print(f"PPT saved to: {result['ppt']}")
        """
        try:
            logger.info(f"Starting PPT generation for: '{user_input}'")
            
            # Step 1: Generate outline
            logger.info("Step 1/3: Generating outline with LLM...")
            outline = self.outline_generator.generate_outline(
                user_input=user_input,
                template_id=template_id,
                author=author,
                max_slides=max_slides,
                temperature=temperature,
            )
            logger.info(
                f"Outline generated: {len(outline.slides)} slides, "
                f"template: {outline.template_id}"
            )

            # Step 2: Validate template exists
            logger.info("Step 2/3: Validating template...")
            template = self.template_loader.load_template(outline.template_id)
            logger.info(f"Using template: {template.template_name}")

            # Step 3: Generate PPT
            logger.info("Step 3/3: Generating PPT file...")
            
            # Prepare output directory
            if output_dir is None:
                output_dir = Path(settings.output_dir)
            ensure_dir(output_dir)

            # Generate PPT
            ppt_filename = f"{outline.outline_id}.pptx"
            ppt_path = output_dir / ppt_filename
            
            generated_ppt_path = self.ppt_generator.generate(
                outline=outline,
                output_path=ppt_path,
                template=template,
            )

            result = {"ppt": generated_ppt_path}

            # Save outline if requested
            if save_outline:
                outline_filename = f"{outline.outline_id}.json"
                outline_path = output_dir / outline_filename
                
                outline_dict = outline.model_dump(mode="json")
                outline_dict["metadata"]["generated_at"] = outline.metadata.generated_at.isoformat()
                
                save_json(outline_dict, outline_path)
                result["outline"] = outline_path
                logger.info(f"Outline saved to: {outline_path}")

            logger.info(f"✅ PPT generation completed successfully!")
            logger.info(f"   PPT file: {generated_ppt_path}")
            logger.info(f"   File size: {generated_ppt_path.stat().st_size / 1024:.1f} KB")

            return result

        except Exception as e:
            logger.error(f"Failed to generate presentation: {e}", exc_info=True)
            raise PPTAgentException(f"Presentation generation failed: {e}")

    def refine_presentation(
        self,
        outline_path: Path,
        user_feedback: str,
        output_dir: Optional[Path] = None,
    ) -> Dict[str, Path]:
        """
        Refine existing presentation based on user feedback
        
        Args:
            outline_path: Path to existing outline JSON
            user_feedback: User's feedback/modification request
            output_dir: Output directory (optional)
        
        Returns:
            Dictionary with paths to refined files
        """
        try:
            logger.info(f"Refining presentation based on feedback: '{user_feedback}'")
            
            # Load existing outline
            from src.utils.file_utils import load_json
            outline_data = load_json(outline_path)
            outline = Outline(**outline_data)
            
            # Refine outline with LLM
            logger.info("Refining outline with LLM...")
            refined_outline = self.outline_generator.refine_outline(
                current_outline=outline,
                user_feedback=user_feedback,
            )
            
            # Generate new PPT
            logger.info("Generating refined PPT...")
            if output_dir is None:
                output_dir = outline_path.parent
            
            ppt_filename = f"{refined_outline.outline_id}_refined.pptx"
            ppt_path = output_dir / ppt_filename
            
            generated_ppt_path = self.ppt_generator.generate(
                outline=refined_outline,
                output_path=ppt_path,
            )
            
            # Save refined outline
            outline_filename = f"{refined_outline.outline_id}_refined.json"
            refined_outline_path = output_dir / outline_filename
            
            outline_dict = refined_outline.model_dump(mode="json")
            outline_dict["metadata"]["generated_at"] = refined_outline.metadata.generated_at.isoformat()
            save_json(outline_dict, refined_outline_path)
            
            logger.info(f"✅ Presentation refined successfully!")
            
            return {
                "ppt": generated_ppt_path,
                "outline": refined_outline_path,
            }
            
        except Exception as e:
            logger.error(f"Failed to refine presentation: {e}", exc_info=True)
            raise PPTAgentException(f"Presentation refinement failed: {e}")

    def list_templates(self) -> list:
        """
        List all available templates
        
        Returns:
            List of template metadata dictionaries
        """
        return self.template_loader.list_templates()

    def get_template_info(self, template_id: str) -> Dict[str, str]:
        """
        Get information about a specific template
        
        Args:
            template_id: Template identifier
        
        Returns:
            Template metadata dictionary
        """
        return self.template_loader.get_template_info(template_id)
