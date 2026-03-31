# ============================================================
# AI Product Sprint - Makefile
# ============================================================

# 项目元数据
PKG_NAME := ai-product-sprint

# 路径
SRC := src
OUTPUT := output

# 默认目标
.DEFAULT_GOAL := help

## help - 显示帮助信息
.PHONY: help
help:
	@echo ""
	@echo "  AI Product Sprint - Makefile"
	@echo ""
	@echo "  可用命令:"
	@echo ""
	@echo "    make install        安装项目 (生产环境)"
	@echo "    make install-dev    安装项目 (开发环境，包含测试依赖)"
	@echo "    make uninstall      卸载项目"
	@echo ""
	@echo "    make run PROJECT=xxx IDEA=xxx   运行 Sprint，例: make run PROJECT=my-app IDEA='做一个 Todo 应用'"
	@echo ""
	@echo "    make test           运行测试"
	@echo "    make lint           代码检查"
	@echo "    make format         代码格式化"
	@echo ""
	@echo "    make clean          清理构建产物"
	@echo "    make clean-output   清理 output 目录"
	@echo "    make clean-all      清理所有生成物（包括 output）"
	@echo ""
	@echo "    make help           显示本帮助信息"
	@echo ""

## install - 安装项目 (生产环境)
.PHONY: install
install:
	uv pip install -e .

## install-dev - 安装项目 (开发环境)
.PHONY: install-dev
install-dev:
	uv pip install -e ".[dev]"

## uninstall - 卸载项目
.PHONY: uninstall
uninstall:
	uv pip uninstall -y $(PKG_NAME)

## run - 运行 Sprint
##   使用方式: make run PROJECT=my-app IDEA='做一个 Todo 应用'
.PHONY: run
run:
ifndef PROJECT
	@echo "错误: 请提供 PROJECT 参数"
	@echo "用法: make run PROJECT=my-app IDEA='你的想法'"
	@exit 1
endif
ifndef IDEA
	@echo "错误: 请提供 IDEA 参数"
	@echo "用法: make run PROJECT=my-app IDEA='你的想法'"
	@exit 1
endif
	uv run python -m src.cli --project "$(PROJECT)" "$(IDEA)"

## test - 运行测试
.PHONY: test
test:
	uv run pytest

## lint - 代码检查
.PHONY: lint
lint:
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check .; \
	elif command -v flake8 >/dev/null 2>&1; then \
		flake8 .; \
	else \
		echo "未找到 lint 工具，请安装 ruff 或 flake8"; \
	fi

## format - 代码格式化
.PHONY: format
format:
	@if command -v ruff >/dev/null 2>&1; then \
		ruff format .; \
	elif command -v black >/dev/null 2>&1; then \
		black .; \
	else \
		echo "未找到格式化工具，请安装 ruff 或 black"; \
	fi

## clean - 清理构建产物
.PHONY: clean
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} \; 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

## clean-output - 清理 output 目录
.PHONY: clean-output
clean-output:
	rm -rf $(OUTPUT)/*

## clean-all - 清理所有生成物
.PHONY: clean-all
clean-all: clean clean-output
