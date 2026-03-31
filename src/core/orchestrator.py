"""Sprint Orchestrator - Manages the overall sprint flow."""

import asyncio
import re
import subprocess
from pathlib import Path
from typing import Optional

from ..agents.types import SprintContract, SprintResult, EvalResult
from ..agents.planner import PlannerAgent
from ..agents.generator import GeneratorAgent
from ..agents.evaluator import EvaluatorAgent
from ..core.config import config


class StreamHandler:
    """处理流式输出，显示实时进度."""

    @staticmethod
    def print_progress(message) -> None:
        """打印进度信息."""
        print(f"   {message}", flush=True)

    @staticmethod
    def print_tool_use(block) -> None:
        """打印工具调用信息."""
        name = block.name
        if name == "Write":
            file_path = block.input.get("file_path", "unknown")
            StreamHandler.print_progress(f"📝 写入文件: {file_path}")
        elif name == "Read":
            file_path = block.input.get("file_path", "unknown")
            StreamHandler.print_progress(f"📖 读取文件: {file_path}")
        elif name == "Bash":
            command = block.input.get("command", "")[:50]
            StreamHandler.print_progress(f"⚡ 执行命令: {command}...")
        elif name == "Edit":
            file_path = block.input.get("file_path", "unknown")
            StreamHandler.print_progress(f"✏️ 编辑文件: {file_path}")
        elif name == "Glob":
            pattern = block.input.get("pattern", "")
            StreamHandler.print_progress(f"🔍 搜索文件: {pattern}")
        elif name.startswith("mcp__playwright__"):
            action = name.replace("mcp__playwright__", "")
            StreamHandler.print_progress(f"🌐 Playwright: {action}")
        else:
            StreamHandler.print_progress(f"🔧 调用工具: {name}")


class SprintOrchestrator:
    """Orchestrates the entire sprint flow."""

    def __init__(self, project_name: str):
        self.project_name = self._sanitize_name(project_name)
        self.project_dir = config.ensure_output_dir(self.project_name)
        self.feedback_path = self.project_dir / "feedback.txt"
        self.frontend_dir = self.project_dir / "frontend"
        self.backend_dir = self.project_dir / "backend"

        self.planner = PlannerAgent(self.project_dir)
        self.generator = GeneratorAgent(self.project_dir)
        self.evaluator = EvaluatorAgent(self.project_dir)

        self.frontend_process: Optional[subprocess.Popen] = None
        self.backend_process: Optional[subprocess.Popen] = None

        self.stream_handler = StreamHandler()

    def _sanitize_name(self, name: str) -> str:
        """将项目名转换为合法的目录名."""
        name = re.sub(r"[^\w\s-]", "", name)
        name = re.sub(r"[-\s]+", "-", name)
        return name.lower()[:50]

    async def run(self, user_idea: str, max_retries: int = None) -> SprintResult:
        """运行完整的 Sprint 流程."""
        if max_retries is None:
            max_retries = config.max_retries

        print(f"\n{'='*60}")
        print(f"🚀 AI Product Sprint: {self.project_name}")
        print(f"{'='*60}\n")

        # Step 1: Planner 生成规格
        print("📋 Step 1: Planner - 生成产品规格...")
        spec_path = await self.planner.run(user_idea, self.stream_handler)
        print(f"   ✅ 规格已生成\n")

        # Step 2: Sprint Contract 协商
        print("📝 Step 2: Sprint Contract - 协商完成标准...")
        contract = await self._negotiate_contract(spec_path)
        print(f"   ✅ 达成 {len(contract.generator_goals)} 个目标\n")

        # Step 3: 多轮 Sprint 循环
        print(f"🔄 Step 3: Sprint 循环（最多 {max_retries} 轮）")
        files = []
        for attempt in range(max_retries):
            print(f"\n{'='*40}")
            print(f"   Sprint {attempt + 1}/{max_retries}")
            print(f"{'='*40}\n")

            # 3a: Generator 生成/修复代码
            if attempt == 0:
                print("🔨 Generator - 生成代码...\n")
                files = await self.generator.run(spec_path, contract, self.stream_handler)
            else:
                feedback = self._read_feedback()
                print(f"🔨 Generator - 修复问题 ({len(feedback)} 项反馈)...\n")
                files = await self.generator.fix(feedback, contract, self.stream_handler)

            print(f"\n   ✅ 生成了/修复了 {len(files)} 个文件\n")

            # 3b: 启动服务器
            print("🚀 启动服务器...")
            await self._start_servers()
            print("   ⏳ 等待服务器就绪...")
            await asyncio.sleep(3)
            print("   ✅ 服务器就绪\n")

            # 3c: Evaluator 测试
            print("🧪 Evaluator - 运行测试...\n")
            result = await self.evaluator.test(contract, self.stream_handler)

            # 3d: 停止服务器
            await self._stop_servers()
            print("   🛑 服务器已停止\n")

            # 3e: 判断结果
            if result.passed:
                print("\n   ✅ 所有测试通过!")
                return SprintResult(
                    success=True,
                    message="Sprint 完成，产品通过所有测试",
                    files_changed=files,
                )
            else:
                print(f"\n   ❌ 测试失败: {len(result.bugs)} 个问题")
                await self._write_feedback(result)

        return SprintResult(
            success=False,
            message=f"超过最大重试次数（{max_retries}）",
            issues=["测试未通过"],
        )

    async def _negotiate_contract(self, spec_path: Path) -> SprintContract:
        """协商 Sprint Contract."""
        contract = SprintContract(
            generator_goals=[
                "实现前端所有页面和组件",
                "实现后端所有 API 端点",
                "确保前后端集成正常",
            ],
            evaluator_criteria=[
                "Design Quality: 设计是否浑然一体？",
                "Originality: 有没有定制设计？",
                "Craft: 技术执行是否良好？",
                "Functionality: 功能是否可用？",
            ],
            test_commands=[
                "浏览器测试：页面加载正常",
                "API 测试：后端响应正常",
            ],
        )
        return contract

    async def _start_servers(self) -> None:
        """启动前后端服务器."""
        if self.backend_dir.exists():
            backend_cmd = ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(config.backend_port)]
            self.backend_process = subprocess.Popen(
                backend_cmd,
                cwd=str(self.backend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        if self.frontend_dir.exists():
            frontend_cmd = ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", str(config.frontend_port)]
            self.frontend_process = subprocess.Popen(
                frontend_cmd,
                cwd=str(self.frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

    async def _stop_servers(self) -> None:
        """停止前后端服务器."""
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process.wait(timeout=5)
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait(timeout=5)

    async def _write_feedback(self, result: EvalResult) -> None:
        """将 Evaluator 的反馈写入文件."""
        content = result.to_markdown()
        self.feedback_path.write_text(content)
        print(f"\n   📝 反馈已写入: {self.feedback_path}")

    def _read_feedback(self) -> str:
        """读取 Evaluator 的反馈."""
        if self.feedback_path.exists():
            content = self.feedback_path.read_text()
            print(f"\n   📖 已读取反馈: {len(content)} 字符")
            return content
        return ""


async def run_sprint(project_name: str, user_idea: str) -> SprintResult:
    """便捷函数：运行完整 Sprint."""
    orchestrator = SprintOrchestrator(project_name)
    return await orchestrator.run(user_idea)
