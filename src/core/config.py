"""Configuration for AI Product Sprint.

Configuration is loaded from Claude Code's settings.json via setting_sources.
"""

from pathlib import Path


class Config:
    """Global configuration."""

    # Path Configuration
    base_dir: Path = Path(__file__).parent.parent.parent
    output_dir: Path = base_dir / "output"

    # Server Configuration
    frontend_port: int = 5173
    backend_port: int = 8000

    # Sprint Configuration
    max_retries: int = 10

    def get_output_dir(self, project_name: str) -> Path:
        """获取项目输出目录."""
        return self.output_dir / project_name

    def ensure_output_dir(self, project_name: str) -> Path:
        """确保输出目录存在."""
        project_dir = self.get_output_dir(project_name)
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir


# Global config instance
config = Config()
