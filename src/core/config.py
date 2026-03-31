"""Configuration for AI Product Sprint.

Configuration is loaded from Claude Code's settings.json via setting_sources.
"""

import sys
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

        if project_dir.exists() and any(project_dir.iterdir()):
            # 目录存在且非空 - 需要交互确认
            print(f"WARNING: 目录 '{project_dir}' 已存在且包含文件。")

            if sys.stdin.isatty():
                # 交互模式：询问用户
                response = input("请选择: [C]ontinue (保留现有文件) / [Q]uit (退出): ").strip().lower()
                if response == 'q':
                    print("已退出。")
                    sys.exit(0)
                # 'c' 或其他任何输入 - 继续执行，使用 exist_ok=True
            else:
                # 非交互模式：自动继续，保留现有文件
                print("非交互模式，自动继续。")
        else:
            # 目录不存在或为空 - 直接创建
            project_dir.mkdir(parents=True, exist_ok=True)

        return project_dir


# Global config instance
config = Config()
