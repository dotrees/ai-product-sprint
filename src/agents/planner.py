"""Planner Agent - Generates product specification from user idea."""

from pathlib import Path

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, ToolUseBlock
from claude_agent_sdk.types import StreamEvent

from ..core.config import config


PLANNER_PROMPT = """你是一个产品规划专家。

你的任务是将用户的简单想法（1-4句话）扩展为完整的产品规格。

项目输出目录：{project_dir}

用户想法：{user_idea}

请生成完整的产品规格，包括：
1. **产品名称** - 简洁有力的名字
2. **一句话描述** - 用一句话概括产品
3. **技术栈** - 前端和后端技术选型
4. **核心功能** - 前端和后端功能列表
5. **页面/路由** - 页面结构和路由规划
6. **数据模型** - 主要数据表/模型设计

重要原则：
- 保持雄心勃勃的范围，不要 under-scope
- 寻找将 AI 功能融入产品的机会
- 专注于高层设计，不要陷入实现细节

请将完整规格输出到 {project_dir}/SPEC.md 文件，格式为 Markdown。"""


class PlannerAgent:
    """Planner Agent - Generates product specification from user idea."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.spec_path = project_dir / "SPEC.md"

    def _create_client(self) -> ClaudeSDKClient:
        """创建 Planner 专用的 Client."""
        options = ClaudeAgentOptions(
            allowed_tools=["Read", "Write", "Bash", "Glob"],
            permission_mode="acceptEdits",
            setting_sources=["user", "project", "local"],
            include_partial_messages=True,
            cwd=str(self.project_dir),
        )
        return ClaudeSDKClient(options=options)

    async def run(self, user_idea: str, stream_handler=None) -> Path:
        """根据用户想法生成产品规格."""
        prompt = PLANNER_PROMPT.format(user_idea=user_idea, project_dir=str(self.project_dir))

        async with self._create_client() as client:
            await client.query(prompt)

            async for message in client.receive_response():
                # 处理流式文本增量 - 直接显示模型输出
                if isinstance(message, StreamEvent):
                    event = message.event
                    if event.get("type") == "content_block_delta":
                        delta = event.get("delta", {})
                        if delta.get("type") == "text_delta":
                            text = delta.get("text", "")
                            print(text, end="", flush=True)

                # 处理工具调用
                elif isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, ToolUseBlock) and stream_handler:
                            stream_handler.print_tool_use(block)

        print()  # 换行
        return self.spec_path


async def run_planner(project_name: str, user_idea: str) -> Path:
    """便捷函数：运行 Planner 并返回规格文件路径."""
    project_dir = config.ensure_output_dir(project_name)
    planner = PlannerAgent(project_dir)
    return await planner.run(user_idea)
