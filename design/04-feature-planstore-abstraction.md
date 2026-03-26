# 特性 1：PlanStore 核心抽象

## 概述

`PlanStore` 是 jcode-plans-py 的核心抽象，作为唯一的公共 API 入口封装了所有计划文档管理功能。

## 概览

`PlanStore` 以不可变数据类（frozen dataclass）的形式提供，用于：
- 创建新的实施计划文件
- 查询现有计划列表
- 管理存储目录初始化

## 设计意图

**解决的问题**：
- 提供统一的接口隐藏文件系统操作细节
- 确保实例创建后状态不可变，避免意外修改
- 统一管理存储路径配置

**设计决策**：
- 使用 `@dataclass(frozen=True)` 实现不可变性
- `working_dir` 和 `letta_home` 在 `__post_init__` 中规范化
- 单一类承担所有职责，简化使用

## 架构

```mermaid
graph TB
    PS[PlanStore<br/>不可变数据类]

    subgraph "属性"
        WD[working_dir: Path]
        LH[letta_home: Path]
        PD[plans_dir: Path<br/>计算属性]
    end

    subgraph "方法"
        CPF[create_plan_file()]
        LP[list_plans()]
        EI[ensure_initialized()]
    end

    PS --> WD
    PS --> LH
    PS --> PD
    PS --> CPF
    PS --> LP
    PS --> EI
```

## 契约（Contract）

| 方面 | 说明 |
|------|------|
| **输入** | `working_dir: Path`, `letta_home: Path \| None` |
| **输出** | 提供 `plans_dir` 计算属性和 CRUD 方法 |
| **副作用** | 首次调用方法时可能创建 `plans_dir` 目录 |
| **错误** | 权限不足时 `create_plan_file` 抛出 `OSError` |
| **幂等** | `ensure_initialized` 多次调用等价于一次 |
| **版本** | v1.0.0 稳定 |

## API 参考

### 类型签名

```python
@dataclass(frozen=True)
class PlanStore:
    working_dir: Path
    letta_home: Path | None = None

    @property
    def plans_dir(self) -> Path: ...

    def create_plan_file(self, project_name: str | None = None) -> Path: ...
    def list_plans(self, project_name: str | None = None) -> list[Path]: ...
    def ensure_initialized(self) -> None: ...
```

### 导入方式

```python
from jcode_plans import PlanStore
```

## 集成矩阵

| 依赖 | 接口语义 | 失败策略 |
|------|----------|----------|
| `jcode-conf-py` | 提供 `LETTA_HOME` 默认值 | 若未安装且 `letta_home=None` 则导入失败 |

## 使用示例

### Algorithm：创建并使用 PlanStore

```
BEGIN
  IMPORT PlanStore FROM jcode_plans
  IMPORT Path FROM pathlib

  # 1. 创建实例
  store = PlanStore(Path.cwd())

  # 2. 首次使用自动初始化目录
  plan_path = store.create_plan_file("my-project")

  # 3. 查询计划
  plans = store.list_plans("my-project")

  # 4. 处理结果
  IF plans NOT EMPTY THEN
    PRINT "Found", LENGTH(plans), "plans"
    PRINT "Latest:", plans[0].name
  END IF
END
```

## 高级主题

### 线程安全性

由于 `frozen=True`，`PlanStore` 实例可安全共享于多线程：

```python
from concurrent.futures import ThreadPoolExecutor

store = PlanStore(Path.cwd())

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(store.list_plans) for _ in range(10)]
    results = [f.result() for f in futures]
    # 所有线程获得相同结果，无竞态条件
```

### 自定义子类

```python
class CustomPlanStore(PlanStore):
    def _default_template(self, project: str) -> str:
        # 自定义模板
        return f"# {project} Plan\n\n## Goals\n\n"
```

## 限制与权衡

| 限制 | 说明 |
|------|------|
| **不可配置模板路径** | 模板硬编码在 `_default_template` 静态方法中 |
| **无连接池** | 直接操作文件系统，每次调用独立 |
| **单存储后端** | 仅支持文件系统，不支持云存储 |

## 相关特性

- [05-feature-filesystem-persistence](05-feature-filesystem-persistence.md) - 底层存储机制
- [09-feature-immutable-dataclass](09-feature-immutable-dataclass.md) - 不可变性实现
