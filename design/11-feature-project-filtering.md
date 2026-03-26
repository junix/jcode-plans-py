# 特性 8：项目过滤查询

## 概述

`list_plans()` 支持通过项目名关键词过滤返回的计划列表，实现按项目隔离和检索计划文档。

## 概览

| 方面 | 说明 |
|------|------|
| **过滤方式** | 子串匹配（`needle in path.name`） |
| **关键词处理** | 消毒后用于匹配 |
| **区分大小写** | 否（取决于文件系统） |

## 设计意图

**解决的问题**：
- 多项目共用存储时的隔离需求
- 快速定位特定项目的计划
- 避免项目名冲突

**设计决策**：
- 简单子串匹配而非精确匹配（灵活性）
- 对关键词消毒避免正则注入
- 大小写敏感（依赖文件系统）

## 架构

```mermaid
graph TB
    subgraph "list_plans 实现"
        GN[glob("*.md")]
        SN["_sanitize_project_name()"]
        FLT[过滤: needle in name]
        SRT[按 st_mtime 排序]
    end

    GN --> FLT
    SN --> FLT
    FLT --> SRT
```

## 契约（Contract）

| 方面 | 说明 |
|------|------|
| **输入** | `project_name: str \| None` |
| **输出** | 过滤后的 `list[Path]` |
| **副作用** | 无 |
| **错误** | 无 |
| **幂等** | 是 |
| **版本** | v1.0.0 稳定 |

## 实现代码

```python
def list_plans(self, project_name: str | None = None) -> list[Path]:
    self.ensure_initialized()
    paths = list(self.plans_dir.glob("*.md"))

    if project_name:
        needle = _sanitize_project_name(project_name)
        paths = [p for p in paths if needle in p.name]

    paths.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return paths
```

## 过滤示例

| 项目名参数 | 消毒后关键词 | 匹配文件 | 不匹配 |
|-----------|-------------|----------|--------|
| `"backend"` | `backend` | `backend-api-...md` | `frontend-ui-...md` |
| `"api"` | `api` | `backend-api-...md`<br/>`api-gateway-...md` | `backend-auth-...md` |
| `"API"` | `API` | 取决于文件系统 | 大多数不匹配 |
| `"v2"` | `v2` | `backend-api-v2-...md` | `backend-api-...md` |

## 集成矩阵

| 依赖 | 接口语义 | 失败策略 |
|------|----------|----------|
| `_sanitize_project_name()` | 字符串消毒 | 永不失败 |

## 使用示例

### Algorithm：过滤查询流程

```
BEGIN FUNCTION list_plans(project_name?)
  # 1. 获取所有计划
  paths = glob("*.md")

  # 2. 如果指定了项目名
  IF project_name IS NOT NULL
    needle = _sanitize_project_name(project_name)
    paths = FILTER paths WHERE needle IN path.name
  END IF

  # 3. 排序
  paths.sort(key=st_mtime, reverse=True)

  RETURN paths
END FUNCTION
```

### Python 示例

```python
store = PlanStore(Path.cwd())

# 创建不同项目的计划
store.create_plan_file("backend-api")
store.create_plan_file("backend-auth")
store.create_plan_file("frontend-web")
store.create_plan_file("frontend-mobile")

# 过滤后端相关
backend = store.list_plans("backend")
print(f"Backend plans: {len(backend)}")  # 2

# 过滤前端相关
frontend = store.list_plans("frontend")
print(f"Frontend plans: {len(frontend)}")  # 2

# 过滤包含 api 的所有计划
api = store.list_plans("api")
print(f"API plans: {len(api)}")  # 1

# 无过滤（全部）
all_plans = store.list_plans()
print(f"All plans: {len(all_plans)}")  # 4
```

### 模糊匹配场景

```python
# 假设有以下计划文件
# - backend-user-service-20260326-xxx.md
# - backend-order-service-20260326-xxx.md
# - backend-api-gateway-20260326-xxx.md

store = PlanStore(Path.cwd())

# 匹配所有 backend 相关
backend = store.list_plans("backend")

# 匹配所有包含 service 的
services = store.list_plans("service")

# 匹配 gateway
gateway = store.list_plans("gateway")
```

## 失败与降级

| 场景 | 行为 |
|------|------|
| `project_name=None` | 返回所有计划 |
| 无匹配 | 返回空列表 |
| 特殊字符 | 自动消毒后匹配 |
| 空字符串 | 消毒为 `project`，返回所有 |

## 高级主题

### 正则匹配替代

```python
import re

def list_plans_regex(store: PlanStore, pattern: str) -> list[Path]:
    """使用正则表达式过滤"""
    all_plans = store.list_plans()
    compiled = re.compile(pattern)
    return [p for p in all_plans if compiled.search(p.name)]
```

### 区分大小写匹配

```python
def list_plans_case_insensitive(store: PlanStore, project_name: str) -> list[Path]:
    """大小写不敏感过滤"""
    needle = _sanitize_project_name(project_name).lower()
    all_plans = store.list_plans()
    return [p for p in all_plans if needle in p.name.lower()]
```

### 多项目查询

```python
def list_multi_project(store: PlanStore, *projects: str) -> dict[str, list[Path]]:
    """一次查询多个项目"""
    return {p: store.list_plans(p) for p in projects}

# 使用
results = list_multi_project(store, "backend", "frontend", "infra")
```

## 限制与权衡

| 限制 | 说明 |
|------|------|
| **子串匹配可能过度** | `api` 匹配 `backend` 中的 `api` |
| **大小写敏感** | `backend` 不匹配 `Backend` |
| **无 OR/AND 逻辑** | 仅支持单一关键词 |
| **无模糊匹配** | 不支持通配符 |

## 相关特性

- [06-feature-file-naming-convention](06-feature-file-naming-convention.md) - 命名规范
- [10-feature-time-based-sorting](10-feature-time-based-sorting.md) - 时间排序
