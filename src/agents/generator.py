"""Generator Agent - Generates frontend and backend code from SPEC.md."""

import json
from pathlib import Path

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, ToolUseBlock, ResultMessage, UserMessage
from claude_agent_sdk.types import StreamEvent

from .types import SprintContract
from ..core.config import config


GENERATOR_PROMPT = """你是一个全栈工程师。

你的任务是根据 SPEC.md 生成完整的 React + FastAPI 前后端代码。

重要提醒：
1. 先读取 SPEC.md 了解产品需求
2. 创建 frontend/ 目录，用 Vite + React 初始化前端项目
3. 创建 backend/ 目录，用 FastAPI 初始化后端项目
4. 实现 SPEC 中要求的所有功能
5. 确保代码完整可运行
6. **生成代码后，必须检查每个文件的完整性**
7. 完成后报告你创建了哪些文件

完整性检查要求：
- 确保括号匹配 {{}} [] ()
- 确保文件以完整语句结尾（不是截断的）
- 如果发现不完整的文件，立即修复

工作目录：{project_dir}

技术栈要求：
- 前端：React + Vite + TypeScript
- 后端：FastAPI + SQLite (或 PostgreSQL)
- 使用现代、干净的设计，不要 AI slop 模式（紫色渐变+白色卡片等）

请开始生成代码。"""


GENERATOR_FEEDBACK_PROMPT = """你需要修复上次生成代码中的问题。

上次评测发现以下问题：
{feedback}

请修复这些问题。读取你的代码，理解问题，然后进行修复。

工作目录：{project_dir}

完成后报告你修改了哪些文件。"""


class GeneratorAgent:
    """Generator Agent - Generates code from specification."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.frontend_dir = project_dir / "frontend"
        self.backend_dir = project_dir / "backend"
        self.spec_path = project_dir / "SPEC.md"
        self.feedback_path = project_dir / "feedback.txt"
        self.session_path = project_dir / ".aisprint" / "session.json"
        self.session_data = self._load_session()

    def _load_session(self) -> dict:
        """加载保存的 session 数据."""
        if self.session_path.exists():
            return json.loads(self.session_path.read_text())
        return {}

    def _save_session(self, session_id: str, checkpoint_id: str):
        """保存 session 数据用于 resume."""
        self.session_path.parent.mkdir(parents=True, exist_ok=True)
        self.session_path.write_text(json.dumps({
            "session_id": session_id,
            "checkpoint_id": checkpoint_id,
        }, indent=2))

    def _create_client(self) -> ClaudeSDKClient:
        """创建 Generator 专用的 Client."""
        options = ClaudeAgentOptions(
            enable_file_checkpointing=True,  # 启用 checkpoint
            resume=self.session_data.get("session_id"),  # Resume session if available
            allowed_tools=["Read", "Write", "Edit", "Bash", "Glob"],
            permission_mode="acceptEdits",
            setting_sources=["user", "project", "local"],
            include_partial_messages=True,
            extra_args={"replay-user-messages": None},  # 接收 checkpoint UUID
            cwd=str(self.project_dir),
        )
        return ClaudeSDKClient(options=options)

    async def run(self, spec_path: Path, contract: SprintContract, stream_handler=None) -> list[str]:
        """根据规格和 Sprint Contract 生成代码."""
        self.frontend_dir.mkdir(exist_ok=True)
        self.backend_dir.mkdir(exist_ok=True)

        prompt = GENERATOR_PROMPT.format(project_dir=str(self.project_dir))

        if contract.generator_goals or contract.evaluator_criteria:
            prompt += f"\n\n## Sprint Contract\n"
            prompt += f"\n{contract.to_markdown()}"

        created_files = []
        session_id = None
        checkpoint_id = None

        async with self._create_client() as client:
            await client.query(prompt)

            async for message in client.receive_response():
                # 处理流式文本增量
                if isinstance(message, StreamEvent):
                    event = message.event
                    if event.get("type") == "content_block_delta":
                        delta = event.get("delta", {})
                        if delta.get("type") == "text_delta":
                            text = delta.get("text", "")
                            print(text, end="", flush=True)
                elif isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, ToolUseBlock):
                            if stream_handler:
                                stream_handler.print_tool_use(block)
                            if block.name == "Write":
                                file_path = block.input.get("file_path", "")
                                if file_path:
                                    created_files.append(file_path)
                # 获取 session_id 和 checkpoint_id
                elif isinstance(message, ResultMessage) and not session_id:
                    session_id = message.session_id
                elif isinstance(message, UserMessage) and message.uuid and not checkpoint_id:
                    checkpoint_id = message.uuid

        # 保存 session 数据用于 resume
        if session_id and checkpoint_id:
            self._save_session(session_id, checkpoint_id)

        return list(set(created_files))

    async def fix(self, feedback: str, contract: SprintContract, stream_handler=None) -> list[str]:
        """根据反馈修复代码."""
        prompt = GENERATOR_FEEDBACK_PROMPT.format(
            feedback=feedback,
            project_dir=str(self.project_dir),
        )

        modified_files = []

        async with self._create_client() as client:
            await client.query(prompt)

            async for message in client.receive_response():
                # 处理流式文本增量
                if isinstance(message, StreamEvent):
                    event = message.event
                    if event.get("type") == "content_block_delta":
                        delta = event.get("delta", {})
                        if delta.get("type") == "text_delta":
                            text = delta.get("text", "")
                            print(text, end="", flush=True)
                elif isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, ToolUseBlock):
                            if stream_handler:
                                stream_handler.print_tool_use(block)
                            if block.name in ("Write", "Edit"):
                                file_path = block.input.get("file_path", "")
                                if file_path:
                                    modified_files.append(file_path)

        return list(set(modified_files))


async def run_generator(project_name: str, contract: SprintContract) -> list[str]:
    """便捷函数：运行 Generator 并返回生成的文件列表."""
    project_dir = config.get_output_dir(project_name)
    generator = GeneratorAgent(project_dir)
    return await generator.run(project_dir / "SPEC.md", contract)
