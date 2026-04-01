# Resume + Checkpoint 最佳实践

## 问题背景

AI Product Sprint 在代码生成过程中可能中断，需要支持 resume 恢复。

### 场景分析

| 情况 | Agent 是否知道 |
|------|--------------|
| 文件完整 | 是（它写的） |
| 文件半成品 | 否（中断时 Agent 不知道文件不完整） |

## SDK Checkpoint 机制验证结果

### 验证通过的功能

1. **enable_file_checkpointing=True** — 正常工作
2. **session_id + resume** — 上下文完整恢复，Agent 记得之前的工作
3. **checkpoint_id** — 每个 turn 的 UserMessage.uuid 可作为 checkpoint
4. **Agent 能检测半成品** — 读取文件时能准确判断不完整（括号匹配、结尾校验等）

### rewind_files 行为

- **作用**：清除 Agent 的内部文件追踪状态（非物理文件恢复）
- **用途**：让 Agent "忘记" checkpoint 之后的操作
- **结论**：对我们的 use case 价值有限

## 推荐方案：Resume + Agent 自检

```
┌─────────────────────────────────────────────────────────────┐
│  方案：Resume + Agent 自检                                  │
├─────────────────────────────────────────────────────────────┤
│  1. GeneratorAgent 启用 enable_file_checkpointing=True        │
│  2. 保存 session_id 到 .aisprint/session.json              │
│  3. Resume 时使用 resume=session_id                       │
│  4. 让 Agent 先读取文件检查完整性                           │
│  5. 如果不完整，Agent 会自动修复                            │
└─────────────────────────────────────────────────────────────┘
```

### 关键代码模式

```python
class GeneratorAgent:
    def _create_client(self) -> ClaudeSDKClient:
        options = ClaudeAgentOptions(
            enable_file_checkpointing=True,  # 启用 checkpoint
            resume=self.session_data.get("session_id"),  # Resume
            allowed_tools=["Read", "Write", "Edit", "Bash", "Glob"],
            permission_mode="acceptEdits",
            include_partial_messages=True,
            extra_args={"replay-user-messages": None},  # 接收 checkpoint UUID
            cwd=str(self.project_dir),
        )
        return ClaudeSDKClient(options=options)
```

### Session 持久化

```python
# 保存
session_data = {
    "session_id": session_id,
    "checkpoint_id": checkpoint_id,
}
# 写入 .aisprint/session.json

# 恢复时加载
session_data = json.loads(session_path.read_text())
```

## 不需要实现的功能

- **文件 hash 对比**：Agent 能检测半成品，无需手动校验
- **rewind_files**：对我们的 use case 价值有限
- **manifest 跟踪**：依赖 SDK 的 checkpoint 机制即可

## 验证脚本

参见 `verify_sdk_checkpoint.py` — 完整的 SDK checkpoint 机制验证
