# AI Product Sprint

通过多代理 AI 系统，用自然语言描述即可生成完整的应用程序。

## Overview

AI Product Sprint 是一个 CLI 工具，它协调多个 AI 代理（Planner、Generator、Evaluator）协作完成以下工作：

1. **理解意图** — Planner Agent 将你的想法扩展为完整的产品规格说明
2. **生成代码** — Generator Agent 创建 React + FastAPI 完整应用
3. **自动化测试** — Evaluator Agent 使用 Playwright 进行端到端测试
4. **迭代修复** — 基于测试反馈自动修复问题，直到通过验收

整个过程自动完成，你只需提供一个产品想法。

## Features

- **自然语言驱动** — 用中文描述你的想法，即可生成完整应用
- **多代理协作** — Planner、Generator、Evaluator 分工明确，确保质量
- **端到端测试** — Playwright 自动化测试，覆盖功能、设计、可用性
- **迭代优化** — 最多 10 次重试，自动修复发现的问题
- **完整技术栈** — React 19 + FastAPI + TypeScript + SQLite
- **一键启动** — 生成的应用自带启动脚本，可立即运行体验

## Tech Stack

**Core System**
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)
![Claude SDK](https://img.shields.io/badge/Claude%20SDK-Agent%20SDK-purple.svg)

**Generated Applications**
![React](https://img.shields.io/badge/React-19.2.4-61DAFB.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6.svg)
![Vite](https://img.shields.io/badge/Vite-8.0.1-646CFF.svg)
![Zustand](https://img.shields.io/badge/Zustand-5.0.12-FB9704.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green.svg)

## Installation

```bash
# 创建虚拟环境（使用 uv）
uv venv --python 3.12

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
uv pip install -e .
```

## Quick Start

### 基本用法

```bash
# 使用 CLI 运行
python -m src.cli --project todo-app "做一个 Todo 应用，支持项目管理、习惯追踪、数据分析"

# 或安装后直接使用
aisprint --project pinterest "做一个 Pinterest 一样的图片收藏网站"
```

### 工作流程

```
想法输入 → Planner 生成规格说明 → Generator 生成代码 → Evaluator 测试 → 完成/修复
```

### 配置

在 `src/core/config.py` 中可调整以下参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `frontend_port` | 5173 | 前端开发服务器端口 |
| `backend_port` | 8000 | 后端 API 服务器端口 |
| `max_retries` | 10 | 最大迭代次数 |
| `output_dir` | `./output` | 生成项目输出目录 |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Sprint Orchestrator                     │
│                  (src/core/orchestrator.py)                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┬───────────────┐
        ▼                   ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│Planner Agent │  │Generator     │  │Evaluator     │
│              │  │Agent         │  │Agent         │
│ src/agents/  │  │src/agents/   │  │src/agents/   │
│ planner.py  │  │generator.py  │  │evaluator.py  │
└──────────────┘  └──────────────┘  └──────────────┘
        │                   │               │
        ▼                   ▼               ▼
   SPEC.md          React + FastAPI    Playwright
                    完整应用代码        自动化测试
```

### Core Components

| 组件 | 文件 | 职责 |
|------|------|------|
| **SprintOrchestrator** | `src/core/orchestrator.py` | 串联整个 Sprint 流程，管理状态与迭代 |
| **PlannerAgent** | `src/agents/planner.py` | 将用户想法扩展为完整的产品规格说明 (SPEC.md) |
| **GeneratorAgent** | `src/agents/generator.py` | 读取规格说明，生成完整的 React + FastAPI 代码 |
| **EvaluatorAgent** | `src/agents/evaluator.py` | 使用 Playwright 进行端到端测试，输出问题列表 |
| **Config** | `src/core/config.py` | 全局配置管理 |

## Project Structure

```
ai-product-sprint/
├── pyproject.toml              # 项目配置
├── README.md                   # 本文档
├── src/
│   ├── cli.py                  # CLI 入口
│   ├── agents/
│   │   ├── planner.py          # Planner Agent
│   │   ├── generator.py        # Generator Agent
│   │   ├── evaluator.py        # Evaluator Agent
│   │   └── types.py            # 共享数据类型
│   └── core/
│       ├── orchestrator.py     # 核心编排器
│       └── config.py           # 配置
└── output/                     # 生成的应用输出目录
    └── todo-app/               # 示例：NexusTodo 应用
        ├── SPEC.md             # 产品规格说明
        ├── frontend/           # React 前端
        │   ├── src/
        │   │   ├── main.tsx    # 前端入口
        │   │   └── App.tsx     # 主组件
        │   └── package.json
        └── backend/            # FastAPI 后端
            ├── main.py        # 后端入口
            └── ...
```

## Generated Application Structure

Sprint 生成的是完整的、可运行的全栈应用：

```
my-app/
├── SPEC.md              # 产品规格说明（由 Planner 生成）
├── frontend/            # React 19 + Vite + TypeScript
│   ├── src/
│   │   ├── main.tsx     # 入口文件
│   │   ├── App.tsx      # 根组件
│   │   ├── pages/       # 页面组件
│   │   ├── components/  # 可复用组件
│   │   └── stores/      # Zustand 状态管理
│   └── package.json
└── backend/             # FastAPI + SQLAlchemy
    ├── main.py          # 入口文件
    ├── routers/          # API 路由
    ├── models/           # 数据模型
    └── requirements.txt
```

## Output Examples

已通过 AI Product Sprint 生成的应用：

### NexusTodo

AI-Native 任务管理平台

- **功能**：自然语言创建任务、AI 任务分解、项目管理、习惯追踪、数据分析
- **技术栈**：React 19 + FastAPI + Zustand + Recharts
- **位置**：`output/todo-app/`

### Super Mario App

示例应用

- **位置**：`output/super-mario-app/`

## License

MIT
