# API 参考与使用

## 概述

jcode-plans-py 提供以 `PlanStore` 为核心的简洁 API，用于创建和查询实施计划文档。

## 入门

### 基本安装

```bash
pip install jcode-plans-py
```

### 基础用法

```python
from pathlib import Path
from jcode_plans import PlanStore

# 创建存储实例
store = PlanStore(Path.cwd())

# 创建新计划
plan_path = store.create_plan_file("my-project")
print(f"Created: {plan_path}")

# 列出所有计划
for plan in store.list_plans():
    print(plan.name)

# 按项目过滤
backend_plans = store.list_plans("backend")
```

## 核心 API

### PlanStore

**签名**：
```python
@dataclass(frozen=True)
class PlanStore:
    working_dir: Path
    letta_home: Path | None = None
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `working_dir` | `Path` | 工作目录（项目根目录），用于派生默认项目名 |
| `letta_home` | `Path \| None` | 计划存储根目录，`None` 时使用 `LETTA_HOME` 环境变量 |

---

### create_plan_file

**签名**：
```python
def create_plan_file(self, project_name: str | None = None) -> Path
```

**参数**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `project_name` | `str \| None` | `None` | 项目名，`None` 时使用 `working_dir.name` |

**返回值**：新创建的计划文件路径

**行为**：
1. 调用 `ensure_initialized()` 确保目录存在
2. 生成格式为 `{project}-{timestamp}-{uuid8}.md` 的文件名
3. 写入包含默认模板的 Markdown 内容

**示例**：
```python
# 使用自动项目名
plan1 = store.create_plan_file()

# 使用指定项目名
plan2 = store.create_plan_file("backend-api")

# 指定子项目
plan3 = store.create_plan_file("backend-api/v2")
```

---

### list_plans

**签名**：
```python
def list_plans(self, project_name: str | None = None) -> list[Path]
```

**参数**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `project_name` | `str \| None` | `None` | 过滤关键词，`None` 时返回所有 |

**返回值**：计划文件路径列表，按修改时间倒序（最新优先）

**示例**：
```python
# 列出所有计划
all_plans = store.list_plans()

# 过滤项目
backend_plans = store.list_plans("backend")

# 模糊匹配
api_plans = store.list_plans("api")
```

---

### ensure_initialized

**签名**：
```python
def ensure_initialized(self) -> None
```

**行为**：确保 `plans_dir` 目录存在，必要时创建（`mkdir(parents=True, exist_ok=True)`）

---

## 常见模式

### 模式 1：创建并立即编辑

```python
from jcode_plans import PlanStore
from pathlib import Path

store = PlanStore(Path.cwd())
plan_path = store.create_plan_file("my-feature")

# 读取并编辑
content = plan_path.read_text()
# ... 添加计划内容 ...
plan_path.write_text(content)
```

### 模式 2：查找最新计划

```python
store = PlanStore(Path.cwd())
plans = store.list_plans("backend-api")

if plans:
    latest = plans[0]  # 已按时间排序
    print(f"Latest plan: {latest}")
```

### 模式 3：批量创建计划

```python
store = PlanStore(Path.cwd())

projects = ["frontend", "backend", "infra"]
for project in projects:
    store.create_plan_file(project)

# 验证
for plan in store.list_plans():
    print(plan.name)
```

## 配置

### 设置自定义存储位置

```python
from pathlib import Path
from jcode_plans import PlanStore

# 使用自定义目录
store = PlanStore(
    working_dir=Path.cwd(),
    letta_home=Path("/tmp/my-plans")
)

# 创建的计划将存储在 /tmp/my-plans/plans/
plan = store.create_plan_file("test")
# -> /tmp/my-plans/plans/test-20260326-143052-a1b2c3d4.md
```

### 环境变量依赖

| 环境变量 | 来源 | 说明 |
|----------|------|------|
| `LETTA_HOME` | `jcode-conf-py` | 默认的计划存储根目录 |

## 最佳实践

### 推荐

```python
# ✓ 使用 Path 对象
store = PlanStore(Path.cwd())

# ✓ 指定清晰的项目名
store.create_plan_file("backend-user-api")

# ✓ 立即处理返回的路径
plan = store.create_plan_file()
content = plan.read_text()
```

### 不推荐

```python
# ✗ 混用字符串和 Path
store = PlanStore("/path/to/project")  # 隐式转换

# ✗ 项目名过长或含特殊字符
store.create_plan_file("my very long project name with spaces!")

# ✗ 依赖默认项目名（可能导致同名冲突）
store.create_plan_file()  # 使用 working_dir.name
```

## 默认计划模板

```markdown
# Implementation Plan

**Project**: {project}

## Overview

## Requirements

## Analysis

## Proposed Changes

## Implementation Steps

## Verification

## Notes
```
