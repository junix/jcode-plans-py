# jcode-plans-py

Plan file storage extracted from `jcode`.

## Installation

```bash
pip install jcode-plans-py
```

## Usage

```python
from pathlib import Path

from jcode_plans import PlanStore

store = PlanStore(Path.cwd())
plan_path = store.create_plan_file()
```
