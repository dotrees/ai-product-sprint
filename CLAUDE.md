# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

AI Product Sprint 是一个多代理 AI 系统，通过 CLI 接口让用户用自然语言描述即可生成完整的 React + FastAPI 应用。

## 常用命令

```bash
# 安装依赖
pip install -e .

# 运行 Sprint
python -m src.cli "做一个 Todo 应用"
python -m src.cli --project my-app "做一个博客系统"
```

## 架构

```
src/core/orchestrator.py (SprintOrchestrator)
       │
       ├── PlannerAgent (planner.py)     → 生成 SPEC.md
       ├── GeneratorAgent (generator.py) → 生成 React + FastAPI 代码
       │         └── fix()              → 根据反馈修复代码
       └── EvaluatorAgent (evaluator.py) → Playwright 端到端测试
```

**核心类型** (`src/agents/types.py`)：
- `SprintContract` — Generator 和 Evaluator 之间的协商协议
- `EvalResult` — Evaluator 测试结果，含 passed/bugs
- `SprintResult` — Sprint 最终结果

## 关键逻辑

1. `orchestrator.run()` 接收 user_idea
2. Planner 生成 `SPEC.md` 到 `output/{project}/SPEC.md`
3. Generator 读取 SPEC.md 生成完整应用到 `frontend/` 和 `backend/`
4. Evaluator 使用 Playwright MCP 工具测试
5. 测试失败时 Generator.fix() 读取 `feedback.txt` 修复，最多循环 `max_retries` 次

## 配置

`src/core/config.py`：`frontend_port`(5173)、`backend_port`(8000)、`max_retries`(10)、`output_dir`

## 注意事项

- Evaluator 使用 `mcp__playwright__*` 工具进行浏览器自动化测试
- `StreamHandler` 在 Agent 执行时打印实时进度
- `output/` 目录是运行产物，已在 `.gitignore` 中排除

## Git 提交要求

- **提交格式**：`type: message`
- **type 可选值**：feat/fix/chore/docs/test/refactor/build/ci/revert
- **message**：可用中文，总长度控制在 180 字符内
- **示例**：`feat: 添加用户登录功能`、`fix: 修复数据导出异常`
