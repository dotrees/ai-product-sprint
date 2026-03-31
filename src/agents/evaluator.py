"""Evaluator Agent - Tests running application with Playwright."""

from pathlib import Path

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock, ToolUseBlock
from claude_agent_sdk.types import StreamEvent

from .types import SprintContract, EvalResult
from ..core.config import config


EVALUATOR_PROMPT = """你是一个 QA 专家。

你的任务是用 Playwright 测试正在运行的应用，验证功能是否正常工作。

测试地址：
- 前端：http://localhost:{frontend_port}
- 后端：http://localhost:{backend_port}

## 四维评估标准（按重要性排序）

### 1. Design Quality（最重要）
设计是否浑然一体？还是零件集合？
- 检查整体视觉一致性
- 检查布局是否协调
- 检查是否有"拼凑感"

### 2. Originality（重要）
有没有自定义决策？还是模板套娃？
- 检查是否使用了默认模板
- 检查是否有创意设计
- 警惕 AI slop 模式（紫色渐变+白色卡片、滥用渐变、通用图标等）

### 3. Craft（技术执行）
- 排版层次
- 间距一致性
- 色彩和谐
- 对比度

### 4. Functionality（功能）
- 用户能否理解界面
- 能否找到主要操作
- 能否完成任务

## 测试步骤

1. 用 browser_navigate 打开前端页面
2. 用 browser_snapshot 查看页面内容
3. 测试核心功能（点击按钮、填写表单等）
4. 用 http_request 测试后端 API
5. 检查 console 是否有错误

## 输出格式

请严格按以下格式输出：

```
passed: true/false
bugs:
- 问题1
- 问题2
report: |
  详细报告...
```

如果所有测试通过，passed 为 true。
如果有任何问题（尤其是 Design Quality 或 Originality），passed 为 false。

注意：即使功能正常，如果设计平庸（AI slop），也要扣分！
"""


class EvaluatorAgent:
    """Evaluator Agent - Tests application with Playwright."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.frontend_dir = project_dir / "frontend"
        self.backend_dir = project_dir / "backend"

    def _create_client(self) -> ClaudeSDKClient:
        """创建 Evaluator 专用的 Client，带 Playwright MCP."""
        options = ClaudeAgentOptions(
            allowed_tools=[
                "Read",
                "Bash",
                # Playwright MCP tools
                "mcp__playwright__browser_navigate",
                "mcp__playwright__browser_snapshot",
                "mcp__playwright__browser_click",
                "mcp__playwright__browser_type",
                "mcp__playwright__http_request",
            ],
            mcp_servers={
                "playwright": {
                    "command": "npx",
                    "args": ["@anthropic-ai/playwright-mcp@latest"],
                }
            },
            permission_mode="acceptEdits",
            setting_sources=["user", "project", "local"],
            include_partial_messages=True,
            cwd=str(self.project_dir),
        )
        return ClaudeSDKClient(options=options)

    async def test(self, contract: SprintContract, stream_handler=None) -> EvalResult:
        """运行测试."""
        prompt = EVALUATOR_PROMPT.format(
            frontend_port=config.frontend_port,
            backend_port=config.backend_port,
        )

        if contract.evaluator_criteria:
            prompt += f"\n\n## Sprint Contract Criteria\n"
            for criterion in contract.evaluator_criteria:
                prompt += f"- {criterion}\n"

        full_text = []

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
                        elif isinstance(block, TextBlock):
                            full_text.append(block.text)

        # 解析结果
        result_text = "\n".join(full_text)
        return self._parse_result(result_text)

    def _parse_result(self, text: str) -> EvalResult:
        """解析 Evaluator 的输出."""
        lines = text.split("\n")

        passed = False
        bugs = []
        report_lines = []
        in_report = False

        for line in lines:
            line = line.strip()

            if line.startswith("passed:"):
                passed = "true" in line.lower()
            elif line.startswith("bugs:"):
                continue
            elif line.startswith("- ") and not in_report:
                bugs.append(line[2:])
            elif line.startswith("report:"):
                in_report = True
                report_content = line[7:].strip()
                if report_content:
                    report_lines.append(report_content)
            elif in_report:
                report_lines.append(line)

        report = "\n".join(report_lines) if report_lines else "No report generated"

        return EvalResult(passed=passed, report=report, bugs=bugs)


async def run_evaluator(project_name: str, contract: SprintContract) -> EvalResult:
    """便捷函数：运行 Evaluator 并返回测试结果."""
    project_dir = config.get_output_dir(project_name)
    evaluator = EvaluatorAgent(project_dir)
    return await evaluator.test(contract)
