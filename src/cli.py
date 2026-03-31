"""CLI entry point for AI Product Sprint."""

import argparse
import asyncio
import sys

from .core.orchestrator import run_sprint
from .core.config import config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Product Sprint - Build products with multi-agent AI system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --project my-app "做一个 Todo 应用"
  %(prog)s --project pinterest "做一个 Pinterest 一样的图片收藏网站"
  %(prog)s --project blog "做一个博客系统"
        """,
    )

    parser.add_argument(
        "idea",
        nargs="+",
        help="Your product idea (as a phrase or sentence)",
    )

    parser.add_argument(
        "--project",
        "-p",
        required=True,
        help="Project name (required)",
    )

    parser.add_argument(
        "--max-retries",
        "-r",
        type=int,
        default=None,
        help=f"Maximum retry attempts (default: {config.max_retries})",
    )

    args = parser.parse_args()

    # 合并 idea 参数
    idea = " ".join(args.idea)

    # 项目名
    project_name = args.project

    # 运行 Sprint
    print(f"\n🎯 Product Idea: {idea}")
    print(f"📁 Project: {project_name}\n")

    result = asyncio.run(run_sprint(project_name, idea))

    # 输出结果
    print(f"\n{'='*60}")
    print(result.to_markdown())

    # 返回退出码
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
