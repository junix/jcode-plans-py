# jcode-plans-py

Filesystem-backed plan document storage, extracted from `jcode`. `PlanStore` creates timestamped Markdown plan files under a configurable plans directory (defaulting to `$LETTA_HOME/plans`), each pre-populated with a structured implementation template. Plans can be listed and filtered by project name, making it easy to organize and retrieve planning documents across multiple projects.

## Build / Test / Install

```bash
just build    # Build wheel with uv
just test     # Run pytest
just install  # Library — no binary to install
```

## Usage

```python
from pathlib import Path

from jcode_plans import PlanStore

# Create a store for the current project
store = PlanStore(Path.cwd())
plan_path = store.create_plan_file()

# Create a plan with an explicit project name
plan_path = store.create_plan_file("my-backend-api")

# List all plans
all_plans = store.list_plans()

# List plans filtered by project name
backend_plans = store.list_plans("my-backend-api")
```

## Dependencies

- [jcode-conf-py](https://github.com/junix/jcode-conf-py) — shared configuration (provides `LETTA_HOME`)
