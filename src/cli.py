"""CLI entry point for AI Product Sprint."""

import argparse
import asyncio
import re
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
  %(prog)s "做一个 Todo 应用"
  %(prog)s "我想做一个 Pinterest 一样的图片收藏网站"
  %(prog)s --project my-app "做一个博客系统"
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
        help="Project name (default: auto-generated from idea)",
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
    project_name = args.project or _generate_project_name(idea)

    # 运行 Sprint
    print(f"\n🎯 Product Idea: {idea}")
    print(f"📁 Project: {project_name}\n")

    result = asyncio.run(run_sprint(project_name, idea))

    # 输出结果
    print(f"\n{'='*60}")
    print(result.to_markdown())

    # 返回退出码
    sys.exit(0 if result.success else 1)


def _generate_project_name(idea: str) -> str:
    """从想法生成项目名."""
    # 取前几个关键词
    words = re.findall(r"\w+", idea)
    if len(words) <= 3:
        name = "-".join(words)
    else:
        name = "-".join(words[:3])

    # 清理
    name = re.sub(r"[^\w-]", "", name)
    name = name.lower()[:30]

    return name or "ai-product"


if __name__ == "__main__":
    main()
